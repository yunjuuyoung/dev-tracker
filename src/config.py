import yaml
from pathlib import Path


class Config:
    """단일 프로젝트 설정 관리"""

    CONFIG_FILE = Path("config.yaml")

    def __init__(self):
        self.config = self._load()

    # ── 로드 ───────────────────────────────────────────────────────

    def _load(self):
        if not self.CONFIG_FILE.exists():
            return self._initial_setup()

        with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}

        return config

    # ── 입력 헬퍼 ─────────────────────────────────────────────────

    def _choose(self, prompt, valid_choices):
        """유효한 값이 입력될 때까지 재입력 요청."""
        while True:
            val = input(prompt).strip()
            if val in valid_choices:
                return val
            print(f"   ⚠️  '{val}'은(는) 올바르지 않습니다. ({'/'.join(valid_choices)} 중 선택)")

    def _ask_path(self, prompt):
        """빈 값이 입력되면 재입력 요청."""
        while True:
            val = input(prompt).strip()
            if val:
                return val
            print("   ⚠️  경로를 입력해 주세요. 빈 값은 사용할 수 없습니다.")

    # ── 초기 설정 ──────────────────────────────────────────────────

    def _initial_setup(self):
        print("=" * 60)
        print("🚀 코드 트래커 초기 설정")
        print("=" * 60)
        print()

        print("📁 감시할 프로젝트 폴더 경로:")
        print("   절대경로 또는 상대경로 모두 사용 가능합니다.")
        print("   예시: C:/workspace/groupware  또는  ../other-project")
        project_path = self._ask_path("   경로: ")

        # scan_paths
        print("\n🔍 특정 하위 폴더만 스캔/감시할까요?")
        print("   1. 아니요 (전체 프로젝트, 기본)")
        print("   2. 네 (특정 경로만)")
        scan_paths = []
        if self._choose("   선택 (1 또는 2): ", ["1", "2"]) == "2":
            print("\n📁 스캔할 경로 입력 (프로젝트 기준 상대경로, 쉼표로 구분)")
            print("   예시: src/main/java, src/main/resources")
            raw = input("   경로: ").strip()
            scan_paths = [p.strip() for p in raw.split(",") if p.strip()]
            if not scan_paths:
                print("   미입력 → 전체 스캔으로 설정합니다.")

        # rescan_on_path_change
        print("\n🔄 프로젝트 경로 변경 시 초기 스캔 재실행할까요?")
        print("   1. 네 (추천!)")
        print("   2. 아니요")
        rescan_on_path_change = self._choose("   선택 (1 또는 2): ", ["1", "2"]) != "2"

        # output_folder
        print("\n📂 변경 로그 저장 위치:")
        print("   1. change_logs (기본)")
        print("   2. 직접 경로 지정")
        if self._choose("   선택 (1 또는 2): ", ["1", "2"]) == "2":
            print("   절대경로 또는 상대경로 모두 사용 가능합니다.")
            print("   예시: C:/logs/changes  또는  ./my_logs")
            output_folder = self._ask_path("   경로: ")
        else:
            output_folder = "change_logs"

        # backup
        print("\n💾 변경 전 파일 자동 백업할까요?")
        print("   1. 네 (추천!)")
        print("   2. 아니요")
        enable_backup = self._choose("   선택 (1 또는 2): ", ["1", "2"]) == "1"
        backup_folder = "file_backups"
        if enable_backup:
            print("\n📂 백업 저장 위치:")
            print("   1. file_backups (기본)")
            print("   2. 직접 경로 지정")
            if self._choose("   선택 (1 또는 2): ", ["1", "2"]) == "2":
                print("   절대경로 또는 상대경로 모두 사용 가능합니다.")
                print("   예시: C:/backups  또는  ../backups")
                backup_folder = self._ask_path("   경로: ")

        # AI
        print("\n🤖 AI로 변경사항을 자동 설명할까요?")
        print("   1. 아니요 (Diff만 기록, 추천!)")
        print("   2. 네 (API 키 필요)")
        use_ai = self._choose("   선택 (1 또는 2): ", ["1", "2"]) == "2"

        ai_provider = "none"
        api_key = ""
        if use_ai:
            print("\n🤖 AI 제공자:")
            print("   1. Google Gemini (무료!)")
            print("   2. OpenAI ChatGPT (유료)")
            print("   3. Ollama (로컬, 무료)")
            ai_provider_map = {"1": "gemini", "2": "chatgpt", "3": "ollama"}
            ai_provider = ai_provider_map[self._choose("   선택 (1, 2, 3): ", ["1", "2", "3"])]

            if ai_provider == "gemini":
                print("\n🔑 Google Gemini API 키:")
                api_key = input("   API Key: ").strip()
            elif ai_provider == "chatgpt":
                print("\n🔑 OpenAI API 키:")
                api_key = input("   API Key: ").strip()
            else:
                print("\n💡 Ollama는 API 키가 필요 없습니다.")
        else:
            print("\n✅ AI 없이 Diff만 기록합니다.")

        # save_session_summary
        print("\n📊 종료 시 세션 요약 파일을 저장할까요?")
        print("   1. 네 (추천!)")
        print("   2. 아니요")
        save_session_summary = self._choose("   선택 (1 또는 2): ", ["1", "2"]) != "2"

        config = {
            'project_path': project_path,
            'scan_paths': scan_paths,
            'rescan_on_path_change': rescan_on_path_change,
            'output_folder': output_folder,
            'enable_backup': enable_backup,
            'backup_folder': backup_folder,
            'use_ai': use_ai,
            'ai_provider': ai_provider,
            'api_key': api_key,
            'ollama_model': 'llama3.2',
            'ollama_url': 'http://localhost:11434',
            'file_extensions': ['.java', '.js', '.xml', '.jsp', '.html', '.css'],
            'ignore_folders': ['node_modules', 'target', '.git', '.svn', 'build', 'dist'],
            'min_change_lines': 1,
            'save_session_summary': save_session_summary,
        }

        self._save(config)
        print(f"\n✅ 설정 완료: {self.CONFIG_FILE}\n")
        return config

    def _save(self, config):
        with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
