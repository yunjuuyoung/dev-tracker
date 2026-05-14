# 📝 코드 변경사항 자동 문서화 도구

프로젝트의 코드 변경을 실시간으로 감지하고 자동으로 기록합니다.
소스를 형상 관리 툴에 올리지 못할 경우를 위해 편의를 고려하여 개발하였습니다.

---

## ✨ 주요 기능

- ✅ **실시간 파일 변경 감지**: 저장하는 즉시 자동 추적 (IDE atomic save 방식 포함)
- ✅ **백그라운드 초기 스캔**: 시작 시 프로젝트를 스캔해 모든 파일의 원본 상태를 기록
- ✅ **특정 경로만 스캔**: `scan_paths`로 감시 범위를 하위 폴더로 좁힐 수 있음
- ✅ **경로 변경 감지**: 프로젝트 경로가 바뀌면 캐시를 자동 초기화하고 재스캔
- ✅ **상세 Diff 기록**: 무엇이 추가/삭제/변경되었는지 한눈에
- ✅ **AI 자동 설명**: Gemini / ChatGPT / Ollama로 변경 내용을 자동 요약
- ✅ **원본 자동 백업**: 변경 전 원본을 최초 1회 안전하게 보관
- ✅ **세션 요약**: 종료 시 세션 동안 변경된 파일 통계 리포트 (on/off 가능)
- ✅ **날짜별 자동 정리**: 날짜가 바뀌면 마크다운 파일 자동 분리
- ✅ **Windows / Mac 모두 지원**

---

## 🚀 빠른 시작

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

AI 기능을 사용한다면 추가 설치:

```bash
# Google Gemini (무료 티어 제공)
# 결제 등록해야 사용 가능
pip install google-generativeai

# OpenAI ChatGPT (유료)
pip install openai

# Ollama (로컬, 무료)
pip install requests
```

### 2. 실행

```bash
python main.py
```

처음 실행하면 설정 인터뷰가 자동으로 시작됩니다.

### 3. 초기 설정 인터뷰

```
📁 감시할 프로젝트 폴더 경로: C:/workspace/myproject
🔍 특정 하위 폴더만 스캔할까요? 1 (아니요 - 전체)
🔄 경로 변경 시 재스캔할까요?  1 (네)
📂 변경 로그 저장 위치:        1 (기본: change_logs)
💾 자동 백업:                  1 (네)
📂 백업 저장 위치:             1 (기본: file_backups)
📝 저장 방식:                  1 (마크다운)
🤖 AI 사용:                    1 (아니요)
📊 세션 요약 파일 저장:        1 (네)
```

설정은 `config.yaml`로 저장되며 이후 실행 시 자동으로 불러옵니다.

---

## 📖 사용 흐름

### 1. 실행 후 초기 스캔

```
✅ 감시 시작: C:\workspace\myproject
🔍 스캔 범위: 전체 프로젝트
📝 AI 없이 Diff만 기록 (빠르고 간단!)
📁 로그: ...\change_logs
💾 백업: ...\file_backups

🔍 초기 스캔 시작...
✅ 초기 스캔 완료: 142개 파일
```

초기 스캔은 백그라운드에서 실행되며, 스캔 중에도 파일 감시는 즉시 시작됩니다.

### 2. 코딩하면서 저장

```
[프로젝트] 📝 변경 감지: UserController.java
💾 최초 백업: UserController.java
[프로젝트] ✅ 저장 완료
```

같은 파일을 다시 저장하면 백업 없이 변경 로그만 기록됩니다.

### 3. 종료 (Ctrl+C)

```
⏹️  코드 트래커 종료 중...

[프로젝트] 📊 세션 요약
   - 변경된 파일: 5개
   - 총 변경 횟수: 12회
   - 추가: +127 / 삭제: -43
   → 저장: ...\session_summary_20260514_090000.md

✅ 종료 완료
```

---

## 📁 생성되는 파일 구조

```
dev-tracker/
├── config.yaml                          ← 개인 설정 (.gitignore)
├── .tracker_state.json                  ← 마지막 경로 기억 (경로 변경 감지용)
│
├── .code_tracker_cache/
│   └── {프로젝트해시}/
│       ├── backup_registry.json         ← 백업 기록
│       └── {파일해시}.cache             ← 파일별 마지막 내용
│
├── change_logs/
│   ├── changes_2026-05-14.md            ← 날짜별 변경 로그
│   └── session_summary_....md           ← 세션 요약 (설정 시)
│
└── file_backups/
    └── src/.../UserController_original.java  ← 최초 원본
```

---

## 📄 변경 로그 형식

```markdown
## ⏰ 14:30:22 - UserController.java

**파일 경로**: `src/main/java/com/company/UserController.java`

### 📋 AI 분석

- **변경 내용**: getUserById 메서드에 null 체크 로직이 추가되었습니다.
- **변경 이유**: 존재하지 않는 ID 조회 시 NullPointerException 방지를 위한 것으로 보입니다.
- **영향**: 잘못된 ID 요청 시 명확한 404 응답을 반환하게 됩니다.

### 🔍 상세 변경사항

```diff
--- 삭제된 코드
+++ 추가된 코드
@@ -45,6 +45,10 @@
 public User getUserById(Long id) {
-    return userRepository.findById(id);
+    User user = userRepository.findById(id);
+    if (user == null) {
+        throw new NotFoundException("User not found: " + id);
+    }
+    return user;
 }
```
```

---

## ⚙️ config.yaml 설정 항목

| 항목 | 기본값 | 설명 |
|---|---|---|
| `project_path` | (필수) | 감시할 프로젝트 폴더 경로 |
| `scan_paths` | `[]` | 감시할 하위 경로 목록. 비어있으면 전체 스캔 |
| `rescan_on_path_change` | `true` | 경로 변경 시 캐시 초기화 후 재스캔 |
| `output_type` | `markdown` | 저장 형식 (`markdown`) |
| `output_folder` | `change_logs` | 변경 로그 저장 위치 |
| `enable_backup` | `true` | 원본 파일 백업 on/off |
| `backup_folder` | `file_backups` | 백업 파일 저장 위치 |
| `use_ai` | `false` | AI 설명 생성 on/off |
| `ai_provider` | `gemini` | AI 제공자 (`gemini` / `chatgpt` / `ollama`) |
| `api_key` | `''` | AI API 키 |
| `gemini_model` | `gemini-1.5-flash` | Gemini 모델명 (무료: `gemini-1.5-flash`) |
| `ollama_model` | `llama3.2` | Ollama 모델명 |
| `ollama_url` | `http://localhost:11434` | Ollama 서버 주소 |
| `file_extensions` | `.java` 등 | 감시할 파일 확장자 목록 |
| `ignore_folders` | `node_modules` 등 | 무시할 폴더 목록 |
| `min_change_lines` | `1` | 이 줄 수 미만 변경은 기록 안 함 |
| `save_session_summary` | `true` | 종료 시 세션 요약 파일 저장 여부 |

### scan_paths 예시

특정 소스 경로만 감시하고 싶을 때:

```yaml
scan_paths:
  - src/main/java
  - src/main/resources
```

---

## 🤖 AI 설정

### Google Gemini (무료 티어 제공)

```bash
pip install google-generativeai
```

```yaml
use_ai: true
ai_provider: gemini
api_key: 'AIza...'
gemini_model: gemini-1.5-flash   # 무료 티어
# gemini_model: gemini-2.0-flash # 유료 (결제 활성화 필요)
```

> **주의**: `gemini-2.0-flash` 이상은 Google Cloud 프로젝트에서 결제를 활성화해야 사용 가능합니다. 무료로 사용하려면 `gemini-1.5-flash`를 사용하세요.

### OpenAI ChatGPT

```bash
pip install openai
```

```yaml
use_ai: true
ai_provider: chatgpt
api_key: 'sk-...'
```

### Ollama (로컬, 완전 무료)

```bash
pip install requests
```

```yaml
use_ai: true
ai_provider: ollama
ollama_model: llama3.2
ollama_url: http://localhost:11434
```

---

## 🐛 문제 해결

### AI 설명이 기록되지 않음

시작 로그에서 확인:
```
❌ AI 초기화 실패: google-generativeai가 설치되지 않았습니다.
```
→ `pip install google-generativeai` 실행

### Gemini Quota exceeded (limit: 0) 오류

`gemini-2.0-flash` 등 최신 모델은 무료 티어에서 사용 불가:
```yaml
gemini_model: gemini-1.5-flash   # 이 값으로 변경
```

### 파일 수정해도 변경 감지 안 됨

- 프로그램을 재시작해보세요.
- `scan_paths`가 설정된 경우 해당 경로 안의 파일인지 확인하세요.
- `file_extensions`에 해당 확장자가 포함되어 있는지 확인하세요.

### 백업을 처음부터 다시 하고 싶다면

`.code_tracker_cache/{프로젝트해시}/backup_registry.json` 삭제 후 재실행.

### 초기 스캔을 다시 하고 싶다면

`.code_tracker_cache/` 폴더 전체 삭제 후 재실행.

---

## 🔨 추가 예정

- [ ] 백업 및 변경 이력을 바탕으로 AI를 통한 인수인계서 자동 작성
