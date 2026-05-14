# 🚀 빠른 시작 가이드 

## ✨ API 키 없이 바로 사용!

---

## Windows 실행

### 1. 터미널 열기
폴더에서 주소창에 `cmd` 입력

### 2. 패키지 설치
```cmd
pip install -r requirements.txt
```

### 3. 실행
```cmd
python main.py
```

---

## Mac 실행

### 1. 터미널 열기
폴더에서 우클릭 → "폴더에서 새로운 터미널"

### 2. 패키지 설치
```bash
pip3 install -r requirements.txt
```

### 3. 실행
```bash
python3 main.py
```

---

## 🎯 초기 설정 (자동)

프로그램 실행 시:

```
📁 감시할 프로젝트 폴더 경로:
   → test_project 폴더 경로 입력

📝 저장 방식:
   → 1 (마크다운)

🤖 AI로 변경사항을 자동 설명할까요?
   → 1 (아니요 - 추천!)
```

**끝! 바로 사용 시작!**

---

## 🤖 AI 추가하고 싶다면? 

### Google Gemini (무료)

1. **API 키 발급**: https://aistudio.google.com/app/apikey
2. **라이브러리 설치**:
```bash
pip install google-generativeai
```
3. **설정 수정** (`config.yaml`):
```yaml
use_ai: true
ai_provider: gemini
api_key: your-key-here
```

### Ollama (로컬, 무료)

1. **설치**: https://ollama.com/download
2. **모델 다운로드**:
```bash
ollama pull llama3.2
```
3. **설정 수정**:
```yaml
use_ai: true
ai_provider: ollama
```

---

## ⚙️ 설정 변경

### 추적 파일 추가
`config.yaml`:
```yaml
file_extensions:
  - .java
  - .properties  # 추가
  - .yml         # 추가
```

### 폴더 무시
```yaml
ignore_folders:
  - node_modules
  - logs  # 추가
```

### AI 켜기/끄기
```yaml
use_ai: false  # false = Diff만, true = AI 설명 추가
```

---

## 💡 사용 팁

### 1. 하루 작업 정리
퇴근 전 `change_logs/changes_오늘.md` 확인 → 일일 보고서 작성

### 2. 커밋 전 리뷰
변경 로그 확인 → 불필요한 수정 제거 → 깔끔한 커밋

### 3. 버그 추적
"어제 뭘 고쳤더라?" → 변경 로그 확인 → 빠른 원인 파악

---

## 🎉 시작!

```bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. 실행
python main.py

# 3. 코딩!
```

**API 키 없이 바로 사용 가능!** 🚀

---
