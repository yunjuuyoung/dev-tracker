# 빠른 시작 가이드

## API 키 없이 바로 사용!

---

## Windows 실행

### 터미널

폴더에서 주소창에 `cmd` 입력 후:

```cmd
pip install -r requirements.txt
python main.py
```

---

## Mac 실행

폴더에서 우클릭 → "폴더에서 새로운 터미널"

```bash
pip3 install -r requirements.txt
python3 main.py
```

---

## 초기 설정 (첫 실행 시 자동)

`config.yaml`이 없으면 아래 순서로 설정을 입력합니다.

```
📁 감시할 프로젝트 폴더 경로:
   → C:/workspace/my-project  (절대경로 또는 상대경로)

🔍 특정 하위 폴더만 스캔할까요?
   → 1 (아니요, 전체 프로젝트)

🔄 경로 변경 시 초기 스캔 재실행할까요?
   → 1 (네, 추천!)

📂 변경 로그 저장 위치:
   → 1 (change_logs, 기본)

💾 변경 전 파일 자동 백업할까요?
   → 1 (네, 추천!)

🤖 AI로 변경사항을 자동 설명할까요?
   → 1 (아니요, 추천! - API 키 불필요)

📊 종료 시 세션 요약 파일을 저장할까요?
   → 1 (네, 추천!)
```

설정 완료 후 바로 파일 감시가 시작됩니다. **Ctrl+C**로 종료.

---

## 생성되는 파일

| 경로 | 내용 |
|---|---|
| `change_logs/changes_날짜.md` | 일별 변경 로그 (Diff 포함) |
| `change_logs/session_summary_날짜시간.md` | 세션 통계 요약 |
| `file_backups/` | 변경 전 원본 파일 백업 |

---

## AI 추가하고 싶다면?

### Google Gemini (무료)

1. API 키 발급: https://aistudio.google.com/app/apikey
2. 라이브러리 설치:
```bash
pip install google-generativeai
```
3. `config.yaml` 수정:
```yaml
use_ai: true
ai_provider: gemini
api_key: your-key-here
```

### OpenAI ChatGPT (유료)

1. API 키 발급: https://platform.openai.com/api-keys
2. 라이브러리 설치:
```bash
pip install openai
```
3. `config.yaml` 수정:
```yaml
use_ai: true
ai_provider: chatgpt
api_key: your-key-here
```

### Ollama (로컬, 무료)

1. 설치: https://ollama.com/download
2. 모델 다운로드:
```bash
ollama pull llama3.2
```
3. `config.yaml` 수정:
```yaml
use_ai: true
ai_provider: ollama
```

---

## 설정 변경 (config.yaml)

### 특정 폴더만 감시
```yaml
scan_paths:
  - src/main/java
  - src/main/resources
```

### 추적 파일 확장자 추가
```yaml
file_extensions:
  - .java
  - .xml
  - .properties  # 추가
  - .yml         # 추가
```

### 폴더 무시
```yaml
ignore_folders:
  - node_modules
  - target
  - logs  # 추가
```

### 백업 / 세션 요약 끄기
```yaml
enable_backup: false
save_session_summary: false
```

### AI 켜기/끄기
```yaml
use_ai: false  # false = Diff만 기록, true = AI 설명 추가
```

---

## 사용 팁

**하루 작업 정리**: 퇴근 전 `change_logs/changes_오늘.md` 확인 → 일일 보고서 작성

**커밋 전 리뷰**: 변경 로그 확인 → 불필요한 수정 제거 → 깔끔한 커밋

**버그 추적**: "어제 뭘 고쳤더라?" → 변경 로그 확인 → 빠른 원인 파악

**원본 복구**: `file_backups/` 에서 변경 전 파일 복원 가능

---

## 빠른 시작 요약

```bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. 실행 (첫 실행 시 설정 입력)
python main.py

# 3. 코딩! (변경사항 자동 기록)
# Ctrl+C 로 종료
```