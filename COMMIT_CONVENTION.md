# 📋 커밋 컨벤션

## 형식

```
<type>: <제목>

- <세부 내용 (선택)>
- <세부 내용 (선택)>
```

- **제목**: 50자 이내, 명령형으로 작성 (예: "추가", "수정", "삭제")
- **세부 내용**: 변경 이유나 주요 변경점이 많을 때만 작성

---

## 타입 목록

| 이모지 | 타입 | 사용 시점 |
|:---:|---|---|
| ✨ | `feat` | 새 기능 추가 |
| 🐛 | `fix` | 버그 수정 |
| 📝 | `docs` | README, 주석 등 문서만 변경 |
| ♻️ | `refactor` | 동작 변화 없는 코드 구조 개선 |
| 🔧 | `config` | 설정 파일 추가 / 수정 |
| 🗑️ | `remove` | 파일 또는 코드 삭제 |
| 🚀 | `perf` | 성능 개선 |
| 🔒 | `security` | 보안 관련 수정 |
| 🎉 | `init` | 프로젝트 최초 커밋 |

---

## 예시

### 기능 추가
```
✨ feat: 세션 요약 저장 여부 설정값 추가

- save_session_summary 옵션 추가 (기본값: true)
- false 설정 시 콘솔 출력은 유지, 파일 저장만 생략
```

### 버그 수정
```
🐛 fix: Gemini 모델 기본값 수정

- gemini_model 설정값으로 모델명 직접 지정 가능하도록 개선
```

### 문서 수정
```
📝 docs: README AI 설정 섹션 업데이트
```

### 리팩토링
```
♻️ refactor: 백업 레지스트리 파일을 캐시 폴더 내부로 이동

- .backup_registry_{hash}.json → .code_tracker_cache/{hash}/backup_registry.json
- .gitignore 항목 정리
```

### 설정 변경
```
🔧 config: config.example.yaml gemini_model 항목 추가
```

### 최초 커밋
```
🎉 init: 코드 변경사항 자동 문서화 도구 초기 버전

- 실시간 파일 변경 감지 (IDE atomic save 방식 포함)
- 백그라운드 초기 스캔 및 scan_paths 범위 설정
- 경로 변경 시 캐시 자동 초기화 (rescan_on_path_change)
- AI 설명 생성 지원 (Gemini / ChatGPT / Ollama)
- 원본 파일 자동 백업 (최초 1회)
- 세션 요약 리포트 생성 (save_session_summary 설정 가능)
- 날짜별 마크다운 변경 로그
```
