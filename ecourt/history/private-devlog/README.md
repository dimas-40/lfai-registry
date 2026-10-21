# 전자소송(ecfs.scourt.go.kr) 자동화 & 사건관리

박씨의 전자소송 관련 법률 작업(작성/제출/진행상황 확인)을 하나의 워크스페이스로 관리하는 공간.
6개월 이상 지속될 사건 대응을 전제로 만듦 — 사건별로 `cases/` 밑에 폴더 하나씩 쌓는다.

## 왜 여기(buckleychang.com/리걸)인가

박씨 지정 (2026-09-18): buckleychang.com이 "개인→법인 전환, 세금/법무 리스크 판단"을
담당하는 브랜치(CLAUDE.md §2 역할 정의 참조)이므로, 전자소송 등 실제 법률 실무 이력은
`리걸/` 상위 폴더 아래 사건유형별로 정리한다. 처음엔 `dtslib-papyrus/mcp-ecourt/`에
있었으나(SSOT 원칙), 박씨가 "리걸/전자소송" 2단 구조로 이 레포에 전량 이전 지시(2026-09-18) →
이전 완료. `dtslib-papyrus`에는 원본이 남아있지 않음(옮김, 복제 아님 — 필요시 git log로 이력 추적).

PC GUI 자동화 실행 자체(Windows 화면 조작)는 `dtslib-localpc`(`pc-eyes/ScreenPilot`,
`win-gui-mcp-server.py`)의 기존 자산을 그대로 재사용하되, 사건 문서/추적은 여기서 관리.

## 디렉토리

```
mcp-ecourt/
├── README.md          ← 이 파일
├── .env.example        ← 민감정보 템플릿 (실제 .env는 gitignore)
└── cases/
    └── 2026-meritz-damages/   ← 사건별 폴더 (진행 중인 첫 사건)
        ├── 01_소장_v1_원본.md
        ├── 02_소장_v2_수정본.md
        └── STATUS.md
```

## 접근 방식 (검증된 기존 자산 기반)

- **PC 화면 확인**: WSL → `/mnt/c/Windows/.../powershell.exe` 풀패스 직접 호출로 스크린샷 캡처 (2026-09-16 검증됨). `screen-pilot`/`desktop-touch` MCP는 cmd.exe가 WSL PATH에 없어서 연결 실패 상태 — 재연결 필요시 `/mcp` reconnect 요청.
- **브라우저(전자소송) 조작**: Chrome CDP(원격 디버깅 9222포트, WSL에서 게이트웨이 IP로 접속) 방식 우선 검토 — `~/dtslib-papyrus/tools/gmail_cdp.py`, `tools/cdp_ensure.py` 패턴 재사용 (`--remote-allow-origins=*` 필수, 콜드스타트 이슈 이미 해결된 이력 있음).
- **네이티브 Windows 팝업(공동인증서 보안모듈 등)**: CDP로는 못 건드림 — `pc-eyes/ScreenPilot` 또는 `win-gui-mcp-server.py`의 pyautogui 픽셀 클릭으로 폴백.
- **SMS 본인인증**: ADB로 박씨 폰(S25U, `100.103.250.45:5900`) 문자함 조회해서 인증번호 자동 입력 (기존 카카오 SMS 검증 패턴과 동일).

## 자율실행 경계선 (박씨 역할 헌법 준수)

Claude가 다 하되, 딱 2가지는 박씨 본인만 가능:
1. **공동인증서 비밀번호 입력** — 법적 서명수단, 대리입력 불가
2. **인지대/송달료 등 실제 결제 확정** — CLAUDE.md 과금 예외 규정 대상, 접수 직전 최종 확인 필요

나머지(폼 입력, 화면 이동, 로그인, 서류 작성/수정, 진행상황 확인)는 전부 Claude가 처리.

## ⚠️ 확인된 한계 (2026-09-16)

- **WSL→PowerShell 원격 입력(mouse_event/SendKeys) 미작동 확인.** 스크린샷 캡처(`CopyFromScreen`)는 정상 작동하지만, 같은 프로세스에서 보낸 클릭/키입력이 실제 Chrome에 전달되지 않음 — ASCII "TEST123" 입력 테스트로 확정 (아무 것도 안 찍힘). 세션은 분리되지 않은 것으로 보임(스크린샷에 실시간 내용 정상 반영) — 원인은 창 스테이션/포그라운드 포커스 권한 문제로 추정, 미해결.
- 그 동안 사건명/법원 드롭다운이 올바르게 채워진 것은 Claude 자동화가 아니라 **박씨가 직접 PC에서 조작**한 결과였음 (오인 확인됨).
- **당분간 실제 폼 입력은 박씨가 직접, Claude는 스크린샷 확인 + 텍스트 제공 + 진행상황 추적 역할로 운영.** Phase 1에서 desktop-touch/screen-pilot MCP 재연결(cmd.exe PATH 문제 해결) 또는 SendInput+SetForegroundWindow 조합 재시도 필요.

## 로드맵

- [x] Phase 0: 사건 폴더/추적 체계 구축, 소장 초안 v2 보정 (2026-09-16)
- [ ] Phase 1: 전자소송 사용자등록 자동화 (CDP + ADB SMS)
- [ ] Phase 2: 서류제출(소장) 폼 자동입력 MCP 툴화
- [ ] Phase 3: 사건 진행상황 주기적 조회 MCP 툴 (기일/송달 알림 → 텔레그램)
- [ ] Phase 4: 다건 동시 사건 관리 (2번째 사건부터 `cases/` 패턴 재사용 검증)

## 민감정보

- `.env` (gitignore 대상): 전자소송 로그인 ID, CDP 호스트/포트 등
- **공동인증서 비밀번호는 어디에도 저장하지 않음** (env 포함) — 매번 박씨 직접 입력
- 사건 문서(소장 등)에 포함된 개인정보(주소/이름)는 이 레포가 private이므로 그대로 보관
