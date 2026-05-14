import hashlib
import json
import shutil
import time
from pathlib import Path
from watchdog.observers import Observer

from .config import Config
from .handler import CodeChangeHandler


class CodeTracker:
    STATE_FILE = Path('.tracker_state.json')

    def __init__(self):
        self.config_manager = Config()
        self.config = self.config_manager.config
        self.observer = None
        self.handler = None

    def start(self):
        path = Path(self.config['project_path'])
        if not path.exists():
            print(f"❌ 경로를 찾을 수 없습니다: {path}")
            return

        self._handle_path_change()

        print("\n" + "=" * 60)
        print("🚀 코드 트래커 시작")
        print("=" * 60)

        self.observer = Observer()
        self.handler = CodeChangeHandler(self.config)

        self.handler._scan_done.wait()

        self.observer.schedule(self.handler, str(path), recursive=True)
        self.observer.start()
        print(f"👁️  파일 감시 시작 | Ctrl+C 로 종료\n")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n" + "=" * 60)
            print("⏹️  코드 트래커 종료 중...")
            print("=" * 60)
            self.handler.generate_session_summary()
            self.observer.stop()

        self.observer.join()
        print("\n✅ 종료 완료\n")

    # ── 경로 변경 감지 / 캐시 초기화 ──────────────────────────────

    def _handle_path_change(self):
        if not self.config.get('rescan_on_path_change', True):
            self._save_state()
            return

        state = self._load_state()
        last_path = state.get('project_path')
        current_path = str(Path(self.config['project_path']))

        if last_path and last_path != current_path:
            print(f"\n⚠️  프로젝트 경로 변경 감지")
            print(f"   이전: {last_path}")
            print(f"   현재: {current_path}")
            print("   캐시를 초기화합니다...\n")

            old_hash = hashlib.md5(Path(last_path).as_posix().encode()).hexdigest()[:8]
            cache_dir = Path('.code_tracker_cache') / old_hash
            if cache_dir.exists():
                shutil.rmtree(cache_dir)

        self._save_state()

    def _load_state(self):
        if not self.STATE_FILE.exists():
            return {}
        try:
            with open(self.STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_state(self):
        state = self._load_state()
        state['project_path'] = str(Path(self.config['project_path']))
        with open(self.STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
