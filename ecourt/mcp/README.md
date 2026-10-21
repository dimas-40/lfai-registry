# ecourt — 전자소송 자동화 도구 (코드만)

> **사건 자료는 여기 두지 않는다.** 이 레포는 GitHub Pages 로 buckleychang.com 에 공개 서빙된다.
> 사건 자료·개발일지: 로컬 전용 `~/ecourt-private/` (remote 없음)

| 파일 | 역할 |
|---|---|
| `SKILL.md` | 에이전트 체크리스트 사본 (정본: `~/.claude/skills/ecourt-filing/SKILL.md`) |
| `guard.py` | 금지 버튼(문서제출·서명·결제·납부·삭제) 코드 차단 + 글자 확인 후 클릭 `safe_click` |
| `kr_deadline.py` | 불변기간 마감 계산 (초일 불산입, 토·일·공휴일 순연, 2026–27 공휴일 표) |
| `win_cdp.py` | Windows python 러너 — 전용 Chrome(포트 9444, 프로필 `C:\tmp\ecourt-cdp`)을 CDP 로 조작, DOM/글자 기준 |
| `ecourt_mcp.py` | MCP 서버 (`claude mcp add ecourt -s user`) |

## MCP 도구 (조회 전용)

- `ecourt_status` — 전용 Chrome 상태·로그인 여부 (없으면 띄움)
- `ecourt_open_login` — 로그인 화면 → 아이디 → 인증서 창까지. **암호는 박씨**
- `ecourt_service_list(period, appeal_days)` — 전체송달문서 조회 + 수신일 기준 마감 계산
- `ecourt_deadline(received, days)` — 마감 계산만

## 시험 기록

- 2026-09-28: 전용 Chrome + CDP 에서 공동인증서 창 정상 표시 (보안모듈 호환 확인). 첫 실행 시 Chrome 상단
  "이 기기의 다른 앱 및 서비스에 액세스" 권한 **허용** 필요 (허용 전엔 로그인 버튼 disabled)
- 포트 9333 은 티스토리 자동화 Chrome, 9222 는 다른 CDP Chrome 이 사용 중 → 9444 전용
- `ecourt_deadline("2026.09.18", 21)` → 2026-10-12(월) ([사건번호] 실측 일치)
- `ecourt_service_list` 실데이터 파싱: 로그인 후 1회 시험 필요 (미완)

## 다음 (2회차 제출 때 동석 시험)

- `ecourt_prepare_filing(doc_type, body, attachments)` — 관련서류 제출 → 섹션별 등록 → 목록에 추가 → 작성완료 → 최종확인 → **4.전자제출 화면에서 정지**
- `ecourt_capture_receipt` — 접수증 캡처 → `~/ecourt-private/cases/<사건>/`
