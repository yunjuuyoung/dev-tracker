import os
import time
import difflib
import hashlib
import json
import threading
from pathlib import Path
from datetime import datetime
from watchdog.events import FileSystemEventHandler

from .ai_client import AIClient


class CodeChangeHandler(FileSystemEventHandler):
    """파일 변경 이벤트 핸들러"""

    def __init__(self, config):
        self.config = config
        self.project_name = config.get('name', '프로젝트')
        self.project_path = Path(config['project_path'])

        # 프로젝트마다 독립된 캐시 디렉토리 (경로 해시로 구분)
        project_hash = hashlib.md5(self.project_path.as_posix().encode()).hexdigest()[:8]
        self.cache_dir = Path('.code_tracker_cache') / project_hash
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.output_dir = Path(config['output_folder'])
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.enable_backup = config.get('enable_backup', False)
        self.backup_dir = None
        self.backup_registry_file = self.cache_dir / 'backup_registry.json'
        self.backup_registry = self._load_backup_registry()

        if self.enable_backup:
            self.backup_dir = Path(config['backup_folder'])
            self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.use_ai = config.get('use_ai', False)
        self.ai_client = None
        ai_status = self._init_ai(config)

        self.processing_files = set()
        self.change_history = []
        self.session_start_time = datetime.now()
        self._scan_done = threading.Event()

        tag = f"[{self.project_name}]"
        print(f"\n{tag} ✅ 감시 시작: {self.project_path}")
        scan_paths = config.get('scan_paths', [])
        if scan_paths:
            print(f"{tag} 🔍 스캔 범위: {len(scan_paths)}개 경로")
            for sp in scan_paths:
                print(f"   - {sp}")
        else:
            print(f"{tag} 🔍 스캔 범위: 전체 프로젝트")
        print(f"{tag} {ai_status}")
        print(f"{tag} 📁 로그: {self.output_dir.absolute()}")
        if self.enable_backup:
            print(f"{tag} 💾 백업: {self.backup_dir.absolute()}")

        scan_thread = threading.Thread(target=self._background_initial_scan, daemon=True)
        scan_thread.start()

    def _init_ai(self, config):
        if not self.use_ai:
            return "📝 AI 없이 Diff만 기록 (빠르고 간단!)"
        try:
            self.ai_client = AIClient(config)
            provider_names = {
                'gemini': 'Google Gemini (무료)',
                'chatgpt': 'OpenAI ChatGPT',
                'ollama': 'Ollama (로컬)'
            }
            name = provider_names.get(config.get('ai_provider', 'gemini'), 'Unknown')
            return f"🤖 AI 제공자: {name}"
        except Exception as e:
            print(f"\n{'='*50}")
            print(f"❌ AI 초기화 실패: {e}")
            print(f"   → AI 없이 Diff만 기록합니다.")
            print(f"{'='*50}\n")
            self.use_ai = False
            return "📝 AI 없이 Diff만 기록 (초기화 실패)"

    # ── 이벤트 핸들러 ──────────────────────────────────────────────

    def on_modified(self, event):
        if not event.is_directory:
            self._dispatch(Path(event.src_path))

    def on_created(self, event):
        if not event.is_directory:
            self._dispatch(Path(event.src_path))

    def on_moved(self, event):
        if not event.is_directory:
            self._dispatch(Path(event.dest_path))

    def _dispatch(self, file_path: Path):
        if file_path.suffix not in self.config['file_extensions']:
            return
        if any(ignore in file_path.parts for ignore in self.config['ignore_folders']):
            return
        if '.code_tracker_cache' in file_path.parts:
            return
        if not self._is_in_scan_paths(file_path):
            return
        if str(file_path) in self.processing_files:
            return

        try:
            self.processing_files.add(str(file_path))
            time.sleep(0.5)
            self._track_change(file_path)
        finally:
            self.processing_files.discard(str(file_path))

    def _is_in_scan_paths(self, file_path: Path) -> bool:
        """scan_paths가 설정된 경우, 해당 경로 하위의 파일인지 확인."""
        scan_paths = self.config.get('scan_paths', [])
        if not scan_paths:
            return True
        for sp in scan_paths:
            try:
                file_path.relative_to(self.project_path / sp)
                return True
            except ValueError:
                continue
        return False

    # ── 변경 추적 ──────────────────────────────────────────────────

    def _track_change(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                current_content = f.read()

            cache_file = self._get_cache_path(file_path)

            if not cache_file.exists():
                if self.enable_backup:
                    self._backup_file(file_path, current_content)
                self._update_cache(file_path, current_content)
                return

            with open(cache_file, 'r', encoding='utf-8', errors='ignore') as f:
                previous_content = f.read()

            if current_content == previous_content:
                return

            if self.enable_backup:
                self._backup_file(file_path, previous_content)

            diff = self._generate_diff(previous_content, current_content, file_path)

            added_lines = len([l for l in diff.split('\n') if l.startswith('+')])
            removed_lines = len([l for l in diff.split('\n') if l.startswith('-')])
            total_changes = added_lines + removed_lines

            if total_changes < self.config['min_change_lines']:
                self._update_cache(file_path, current_content)
                return

            print(f"[{self.project_name}] 📝 변경 감지: {file_path.name}")

            explanation = None
            if self.use_ai and self.ai_client:
                explanation = self._generate_ai_explanation(file_path, diff)

            relative_path = file_path.relative_to(self.project_path)
            self.change_history.append({
                'timestamp': datetime.now(),
                'file_path': str(relative_path),
                'file_name': file_path.name,
                'added_lines': added_lines,
                'removed_lines': removed_lines,
                'total_changes': total_changes
            })

            self._save_change_log(file_path, diff, explanation)
            print(f"[{self.project_name}] ✅ 저장 완료\n")

            self._update_cache(file_path, current_content)

        except Exception as e:
            print(f"❌ 오류 발생: {file_path.name} - {str(e)}\n")

    # ── 캐시 ───────────────────────────────────────────────────────

    def _get_cache_path(self, file_path):
        relative_path = file_path.relative_to(self.project_path)
        path_hash = hashlib.md5(str(relative_path).encode()).hexdigest()
        return self.cache_dir / f"{path_hash}.cache"

    def _update_cache(self, file_path, content):
        cache_file = self._get_cache_path(file_path)
        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write(content)

    # ── 백업 ───────────────────────────────────────────────────────

    def _load_backup_registry(self):
        if self.backup_registry_file.exists():
            try:
                with open(self.backup_registry_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_backup_registry(self):
        with open(self.backup_registry_file, 'w', encoding='utf-8') as f:
            json.dump(self.backup_registry, f, indent=2, ensure_ascii=False)

    def _backup_file(self, file_path, content):
        try:
            relative_path = file_path.relative_to(self.project_path)
            file_key = str(relative_path)

            if file_key in self.backup_registry:
                backup_path = Path(self.backup_registry[file_key]['backup_path'])
                if backup_path.exists():
                    return
                print(f"💾 백업 파일 재생성: {file_path.name}")

            backup_file_dir = self.backup_dir / relative_path.parent
            backup_file_dir.mkdir(parents=True, exist_ok=True)

            backup_file_name = f"{file_path.stem}_original{file_path.suffix}"
            backup_file_path = backup_file_dir / backup_file_name

            with open(backup_file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            self.backup_registry[file_key] = {
                'backup_path': str(backup_file_path),
                'backup_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'original_path': str(file_path)
            }
            self._save_backup_registry()
            print(f"💾 최초 백업: {file_path.name}")

        except Exception as e:
            print(f"⚠️  백업 실패: {file_path.name} - {str(e)}")

    # ── 초기 스캔 ──────────────────────────────────────────────────

    def _background_initial_scan(self):
        tag = f"[{self.project_name}]"
        scan_paths = self.config.get('scan_paths', [])
        if scan_paths:
            roots = [self.project_path / sp for sp in scan_paths]
            print(f"{tag} 🔍 초기 스캔 시작... ({len(roots)}개 경로)")
        else:
            roots = [self.project_path]
            print(f"{tag} 🔍 초기 스캔 시작...")

        scanned_count = 0

        try:
            for root_path in roots:
                if not root_path.exists():
                    print(f"⚠️  스캔 경로를 찾을 수 없습니다: {root_path}")
                    continue

                for root, dirs, files in os.walk(root_path):
                    dirs[:] = [d for d in dirs if d not in self.config['ignore_folders']]

                    for file in files:
                        file_path = Path(root) / file
                        if file_path.suffix not in self.config['file_extensions']:
                            continue

                        cache_file = self._get_cache_path(file_path)
                        if cache_file.exists():
                            continue

                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            self._update_cache(file_path, content)
                            scanned_count += 1
                        except Exception:
                            continue

            print(f"{tag} ✅ 초기 스캔 완료: {scanned_count}개 파일 \n")
            self._scan_done.set()

        except Exception as e:
            print(f"{tag} ⚠️  초기 스캔 오류: {e}")
            self._scan_done.set()

    # ── Diff / AI ──────────────────────────────────────────────────

    def _generate_diff(self, previous, current, file_path):
        diff = difflib.unified_diff(
            previous.splitlines(keepends=True),
            current.splitlines(keepends=True),
            fromfile='삭제된 코드',
            tofile='추가된 코드',
            lineterm='\n'
        )
        return ''.join(diff)

    def _generate_ai_explanation(self, file_path, diff):
        try:
            prompt = f"""다음은 그룹웨어 프로젝트의 코드 변경사항입니다.

**파일명**: {file_path.name}
**파일 타입**: {file_path.suffix}

**변경된 코드 (Diff)**:
```diff
{diff[:3000]}
```

이 코드 변경사항을 한국어로 **간단명료하게** 설명해주세요.

다음 형식으로 작성해주세요:
- **변경 내용**: 무엇이 변경되었는지 (1-2문장)
- **변경 이유**: 왜 이런 변경이 필요했을 것 같은지 (1-2문장)
- **영향**: 이 변경이 시스템에 미칠 영향 (1-2문장)

간결하고 핵심만 담아 작성해주세요."""
            return self.ai_client.generate_explanation(prompt)
        except Exception as e:
            return f"⚠️ AI 설명 생성 실패: {str(e)}\n(변경사항은 기록되었습니다)"

    # ── 로그 저장 ──────────────────────────────────────────────────

    def _save_change_log(self, file_path, diff, explanation):
        self._save_to_markdown(file_path, diff, explanation)

    def _save_to_markdown(self, file_path, diff, explanation):
        today = datetime.now().strftime("%Y-%m-%d")
        md_file = self.output_dir / f"changes_{today}.md"

        self.output_dir.mkdir(parents=True, exist_ok=True)

        if not md_file.exists():
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(f"# 코드 변경 로그 - {today}\n\n")
                f.write(f"프로젝트: {self.project_path}\n\n")
                f.write("---\n\n")

        relative_path = file_path.relative_to(self.project_path)
        timestamp = datetime.now().strftime("%H:%M:%S")

        with open(md_file, 'a', encoding='utf-8') as f:
            f.write(f"## ⏰ {timestamp} - {file_path.name}\n\n")
            f.write(f"**파일 경로**: `{relative_path}`\n\n")
            if explanation:
                f.write(f"### 📋 AI 분석\n\n{explanation}\n\n")
            f.write(f"### 🔍 상세 변경사항\n\n")
            f.write(f"```diff\n{diff}\n```\n\n")
            f.write("---\n\n")

    # ── 세션 요약 ──────────────────────────────────────────────────

    def generate_session_summary(self):
        total_files = len(set(item['file_path'] for item in self.change_history))
        total_changes = len(self.change_history)
        total_added = sum(item['added_lines'] for item in self.change_history)
        total_removed = sum(item['removed_lines'] for item in self.change_history)

        if not self.change_history:
            print(f"\n[{self.project_name}] 📊 이번 세션에서 변경된 파일이 없습니다.")
            return

        print(f"\n[{self.project_name}] 📊 세션 요약")
        print(f"   - 변경된 파일: {total_files}개")
        print(f"   - 총 변경 횟수: {total_changes}회")
        print(f"   - 추가: +{total_added} / 삭제: -{total_removed}")

        if not self.config.get('save_session_summary', True):
            return

        session_end_time = datetime.now()
        session_duration = session_end_time - self.session_start_time

        self.output_dir.mkdir(parents=True, exist_ok=True)
        summary_file = self.output_dir / f"session_summary_{self.session_start_time.strftime('%Y%m%d_%H%M%S')}.md"

        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("# 코드 트래커 세션 요약\n\n")
            f.write(f"**시작 시간**: {self.session_start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**종료 시간**: {session_end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**총 작업 시간**: {str(session_duration).split('.')[0]}\n\n")
            f.write("---\n\n## 📊 통계\n\n")
            f.write(f"- **변경된 파일 수**: {total_files}개\n")
            f.write(f"- **총 변경 횟수**: {total_changes}회\n")
            f.write(f"- **추가된 라인**: +{total_added}\n")
            f.write(f"- **삭제된 라인**: -{total_removed}\n")
            f.write(f"- **순 변경**: {total_added - total_removed:+d}\n\n")
            f.write("---\n\n## 📝 변경된 파일 목록\n\n")

            files_dict = {}
            for item in self.change_history:
                fp = item['file_path']
                if fp not in files_dict:
                    files_dict[fp] = {'count': 0, 'added': 0, 'removed': 0, 'times': []}
                files_dict[fp]['count'] += 1
                files_dict[fp]['added'] += item['added_lines']
                files_dict[fp]['removed'] += item['removed_lines']
                files_dict[fp]['times'].append(item['timestamp'])

            for fp, stats in sorted(files_dict.items(), key=lambda x: x[1]['count'], reverse=True):
                f.write(f"### `{fp}`\n\n")
                f.write(f"- **변경 횟수**: {stats['count']}회\n")
                f.write(f"- **추가**: +{stats['added']} 라인\n")
                f.write(f"- **삭제**: -{stats['removed']} 라인\n")
                f.write(f"- **변경 시간**: \n")
                for t in stats['times']:
                    f.write(f"  - {t.strftime('%H:%M:%S')}\n")
                f.write("\n")

            f.write("---\n\n## 📅 시간순 변경 이력\n\n")
            for item in self.change_history:
                time_str = item['timestamp'].strftime('%H:%M:%S')
                f.write(f"- **{time_str}** - `{item['file_name']}` ")
                f.write(f"(+{item['added_lines']} -{item['removed_lines']})\n")

        print(f"   → 저장: {summary_file.absolute()}")
