---
name: project_ecourt_gui_automation_prep
description: 전자소송(ecfs) — [사건번호] 보정서 09-28 접수완료, 답변서/기일 대기. 저장위치 buckleychang.com/리걸/전자소송, screen-pilot MCP 연결됨
metadata: 
  node_type: memory
  type: project
  originSessionId: 1ee131d6-213b-404b-8512-fc1c3dfa7767
  modified: 2026-09-18T01:05:54.662Z
---

박씨가 전자소송(대한민국 법원 전자소송 시스템) 관련 작업을 GUI 자동화로 앞으로 진행 예정. 2026-09-16 최초 화면 확인.

**Why:** 전자소송 PC에서 진행 상태 추적/등록 등을 자동화해야 함 (구체 작업 범위는 아직 미지시, 박씨가 추후 지시 예정).

**확인된 사실 (raw):**
- 사이트: `ecfs.scourt.go.kr` — 대한민국 전자소송 (Korean e-Court e-filing system)
- 최초 확인 화면: `ecfs.scourt.go.kr/psp/index.on?m=PSP102M01` — 사용자등록 1단계(사용자유형선택), 일반사용자 탭
- PC 컴퓨터명: `DTSLIB`
- 화면 해상도: 1280x720
- 브라우저: Chrome, 열린 탭 2개 (전자소송 탭 + "새 채팅 - Claude" 탭) — Claude Code가 같은 PC에서 동작 중

**PC 접근 방법 (중요 — MCP 우회):**
- `screen-pilot`, `desktop-touch` MCP 서버는 `cmd.exe not found in $PATH`로 연결 실패 상태 (WSL PATH에 Windows 경로 없음)
- 우회: WSL bash에서 powershell.exe를 **풀패스로 직접 호출**하면 정상 작동
  - `/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -Command "..."`
- 스크린샷 캡처 확인된 방법:
  ```powershell
  Add-Type -AssemblyName System.Windows.Forms,System.Drawing
  $screens = [System.Windows.Forms.Screen]::AllScreens
  $bounds = [System.Drawing.Rectangle]::Empty
  foreach ($s in $screens) { $bounds = [System.Drawing.Rectangle]::Union($bounds, $s.Bounds) }
  $bmp = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
  $bmp.Save('C:\Temp\pc_screen_now.png', [System.Drawing.Imaging.ImageFormat]::Png)
  ```
  - 저장 후 `cp /mnt/c/Temp/pc_screen_now.png <scratchpad>/` 로 WSL에서 복사 → Read 툴로 열람
- Screen.AllScreens 해상도 조회는 `Add-Type -AssemblyName System.Windows.Forms`를 스크립트 최상단에서 먼저 로드해야 타입 인식됨 (한 명령에서 순서 꼬이면 TypeNotFound 남)

**How to apply:** 전자소송 GUI 자동화 작업 지시 오면 이 파일 먼저 참고. `screen-pilot`/`desktop-touch` MCP 재연결 시도보다 powershell.exe 직접 호출이 즉시 작동하는 경로. 클릭/키입력 자동화는 SendKeys 또는 win32 API 필요 — 아직 미검증, 다음 세션에서 마우스클릭 좌표 자동화 방법 검증 필요.

## 2026-09-16 확정 — 저장소/사건관리 체계

- **저장위치 (2026-09-18 최종 이관)**: `~/buckleychang.com/리걸/전자소송/`. GitHub `dtslib1979/buckleychang.com`(private 확인됨, `gh repo view`로 실측). 박씨 지시: "buckleychang.com에 리걸(상위)/전자소송(하위) 2단 폴더 만들고 이력 전부 옮겨와" — buckleychang.com이 개인→법인전환/세금·법무 리스크 판단 담당 브랜치(레포 CLAUDE.md §2)라 실제 법률 실무는 여기가 맞는 자리. **직전 위치였던 `dtslib-papyrus/mcp-ecourt/`는 완전히 제거됨**(papyrus 커밋 11752b6, buckleychang.com 커밋 f04f013) — 더 이상 papyrus 경로 참조하지 말 것.
  - 새 경로: `~/buckleychang.com/리걸/전자소송/{README.md, cases/, tools/, .env.example, 072-*.md(개발일지)}`
  - Windows GUI 자동화 실행 자산(pc-eyes, win-gui-mcp-server.py)은 여전히 `dtslib-localpc`에 둠 — 이 구분은 안 바뀜.
- 이미 존재하던 자산 재사용: `pc-eyes/ScreenPilot/`(mouse/keyboard/scroll/screen_capture 코어), `win-gui-mcp-server.py`(pyautogui 기반 MCP stdio 서버, 이미 완성된 패턴) — 이 둘을 기반으로 ecourt 전용 MCP 툴을 확장할 예정. 새로 처음부터 안 만듦.
- 브라우저(웹사이트) 조작은 CDP 우선(픽셀 클릭보다 견고) — `~/dtslib-papyrus/tools/gmail_cdp.py`, `tools/cdp_ensure.py` 패턴 재사용. 네이티브 팝업(공동인증서 보안모듈)만 픽셀 클릭 폴백.
- **사건 폴더 구조**: `ecourt-mcp/cases/<사건식별자>/` 밑에 소장 버전별 md + `STATUS.md`(진행로그). 첫 사건: `2026-meritz-damages` (원고 [원고] vs [상대방 보험사], 손해배상(자) 2,200,000원, 2026-09-01 인천 남동구 만수동 접촉사고). 6개월 이상 갈 수 있는 사건이라 세션 넘어 이 폴더에서 계속 이어감.
- **자율실행 경계선 (박씨 역할 헌법에도 불구하고 예외)**: 공동인증서 비밀번호 입력, 인지대/송달료 실제 결제 확정 — 이 2가지만 박씨 본인 확인 필요. 나머지(폼입력/로그인/서류작성/진행조회)는 Claude가 전부 자동 처리. SMS 본인인증은 ADB로 박씨 폰 문자함 조회해서 대응 가능([[project_adb_sms_kakao_verification]] 패턴).
- 민감정보 규칙: `.env`는 이미 레포 전역 .gitignore로 커버됨(`ecourt-mcp/.env` 자동 제외 확인됨). 공동인증서 비밀번호는 env에도 저장 금지 — 매번 직접 입력.

## 2026-09-16 GUI 자동화 방식 확정 — pyautogui만 사용

- **win32 API 직접호출(mouse_event/SendKeys/SendInput, KEYEVENTF_UNICODE 포함) 전부 실패 확정.** WSL에서 띄운 PowerShell 프로세스로 GetForegroundWindow/WindowFromPoint 찍으면 정확히 Chrome 창이 잡히는데도, 클릭·키입력이 실제로 반영 안 됨(ASCII도 한글도 무반응, 스페이스바만 페이지 스크롤로 반응 — 포커스가 안 잡히는 것으로 추정, 원인 재조사 불필요).
- **해결: pyautogui (Windows Python, `C:\Users\dtsli\AppData\Local\Programs\Python\Python312\python.exe`)는 정상 작동.** `pyautogui.click()` + `pyautogui.hotkey('ctrl','v')` 조합으로 청구취지/청구원인 실제 입력 성공.
- 한글/유니코드 텍스트는 `pyautogui.typewrite()`로 안 됨 — 반드시 `win32clipboard`로 클립보드 세팅 후 Ctrl+V.
- 재사용 코드: `~/buckleychang.com/리걸/전자소송/tools/ecfs_pyauto.py` (click/paste_korean_text/scroll_page/click_sidebar_tab 함수 제공), 좌표/절차 상세: `~/buckleychang.com/리걸/전자소송/tools/COORDINATES.md` (2026-09-18 경로 이관됨)
- **앞으로 ecfs.scourt.go.kr GUI 자동화는 무조건 이 pyautogui 경로만 쓴다. win32 직접호출 재시도 금지.**
- 스크린샷 캡처(CopyFromScreen)는 PowerShell에서도 정상 작동 — 캡처와 입력이 다른 문제였음.

## 2026-09-16 1호 사건 접수 완료 — [사건번호]

[상대방 보험사] 상대 손해배상(자) 소송, [관할 법원]에 정식 접수 완료 확인(접수증명서로 검증). 원고 [원고], 청구금액 2,200,000원, 인지대·송달료 66,000원 결제 완료. 소장/접수증명서 PDF는 `~/buckleychang.com/리걸/전자소송/cases/2026-meritz-damages/04_소장_접수본_[사건번호].pdf`, `05_접수증명서_...pdf`에 정본 보관(2026-09-18 경로 이관됨), 텔레그램 전송도 완료.

**이 세션에서 확립된 워크플로 (다음 사건에도 그대로 적용):**
1. 초안 검토 → 법적 필수요소(입증방법/관할/작성일/서명란) 보정
2. 증거자료는 이메일/카카오톡 등 실제 출처에서 ADB/Gmail로 직접 회수, 법원 인식용 파일명(갑제O호증_내용_촬영일시)으로 정리
3. GUI 자동화는 `ecfs_pyauto.py`(pyautogui)로, 매 클릭 후 반드시 스크린샷으로 결과 확인 — 클릭 한 번에 예상외 페이지 이동이 자주 발생하므로 성급하게 연속 클릭 금지
4. 전자소송은 자동 임시저장되므로 화면이 이상하게 튀어도 데이터 유실 걱정 없이 "나의전자소송>작성중서류"에서 복구 가능
5. 접수 완료 여부는 "나의전자소송 메인화면 > 제증명 발급내역"에서 접수증명서 존재로 최종 확인 (사건번호 발급 = 확정)

## 🔴 2026-09-18 확정 — 전자소송/법률 GUI 작업은 박씨 동석 필수 (예외 규정, 박씨 역할 헌법 상위)

**사고 경위**: 보정명령.pdf를 "다른 이름으로 저장" 다이얼로그에 저장하던 중, `paste_korean_text()`로 파일명 입력창 좌표(700,700)를 스크린샷 확인 없이 추측 클릭 → 실제로는 그 좌표에 입력창이 없어 포커스가 파일탐색기(Downloads 폴더) 배경에 있었음 → Ctrl+A(전체선택)+Ctrl+V가 삭제성 동작으로 오작동 → **Downloads 폴더 219개 항목이 순간적으로 휴지통 이동**. 즉시 발견해서 전량 복구 완료(실질 피해 없음), 원인은 좌표 미확인 후 클릭 — 명백한 Claude 실수.

**박씨 판단(합리적 결론으로 수용)**: 키보드/클립보드 입력 신뢰성이 딥시크/aider 등 외부 도구 경유 시 더 취약해질 수 있고(에이전트가 중고 거래·악용 경로로 넘어갈 경우 위험), Claude Code 자체도 좌표기반 GUI 자동화에서 이런 사고가 날 수 있음이 실측으로 확인됨.

**확정 규칙 (전자소송/법률 관련 PC GUI 작업 전용, 다른 작업에는 적용 안 함)**:
- ecfs.scourt.go.kr GUI 자동화(클릭/붙여넣기/파일저장 등 실제 조작)는 **박씨가 PC 앞에 있고 화면을 지켜보는 상태에서만** 진행한다.
- 공동인증서 로그인은 기존 규정대로 박씨 본인만 가능(변경 없음) — 이번 건으로 추가된 건 "로그인 이후의 GUI 조작 전 과정"도 박씨 동석이 필요하다는 점.
- 박씨가 사무실에 없거나 자리를 비운 상태로 확인되면, GUI 클릭/입력 자동화를 진행하지 않고 먼저 박씨에게 "PC 앞에 와야 진행 가능"이라고 알린다 — 임의로 진행하지 않는다.
- 사건 조회(읽기 전용, 나의사건검색 등)처럼 삭제/제출/결제 위험이 없는 단순 조회는 예외로 동석 없이 진행 가능. 파일 저장/폼 제출/클립보드 조작이 들어가면 전부 동석 필수.
- **이 규정은 "박씨는 말과 의사결정만, 실행은 Claude"라는 글로벌 행정법의 명시적 예외다.** 법률 문서 GUI 작업의 물리적 리스크(오조작으로 인한 파일 손실·오제출)가 크므로 이 영역에서만 예외 적용.

## 2026-09-18 보정명령 대응 진행중 — 다음 세션 이어갈 것

**보정명령 내용 확인 완료**: [사건번호], 21일 이내(2026.09.17 송달 기준) "피고 [상대방 보험사] 주식회사의 법인 등기사항증명서(법인등기부등본)" 제출 요구. 재판부 민사제54단독. PDF는 `~/Downloads/보정명령.pdf`(Windows) + 텔레그램 전송 완료.

**작업 구분 확정(박씨 지시, 2026-09-18)**: 인터넷등기소(iros.go.kr)에서 등본 열람/발급(결제포함)은 **남의 공개정보를 가져오는 것이라 무인 진행 가능** — 이 항목은 위 "GUI 작업 박씨 동석 필수" 규칙의 예외. 단 전자소송에 실제 "제출" 버튼 누르는 것은 동석 필수(변경 없음, 내 문서를 올리는 행위라 리스크 다름).

**진행 상태**: iros.go.kr 접속 → "법인 > 열람·발급" 클릭 → 로그인 화면(일반사용자 탭) 도달 → 공동인증서 보안모듈 접근 권한 팝업(Allow/Block) 뜬 상태에서 박씨가 "시간 걸리니 다음에" 판단, 중단.

**다음에 이어서 할 일**:
1. iros.go.kr 로그인 화면에서 재시작 — 보안모듈 팝업 Allow → 일반사용자 탭 인증서 로그인(박씨 동석 불필요, 남의 정보 열람이라 무인 가능 원칙 적용됨)
2. 법인 열람·발급 메뉴에서 "[상대방 보험사] 주식회사" 검색 → 등기사항증명서 열람/발급 신청 → 결제(수수료 소액) → PDF 다운로드
3. 전자소송(ecfs.scourt.go.kr) "나의전자소송 > 서류제출"에서 보정서 작성 + 등기부등본 첨부까지는 무인 진행 가능
4. **최종 "제출" 버튼은 박씨가 PC 앞에서 확인 후에만 클릭** — 이 단계에서 박씨 호출할 것
5. 기한 여유 있음(21일), 급하지 않음 — 다음 세션(예: 다음주 수요일) 이어가면 됨.

## 2026-09-18 백서 작성 완료 — 교재화 계획

박씨가 사건 전체(개요~미해결과제)를 정리한 백서를 직접 작성해서 전달 →
`~/buckleychang.com/리걸/전자소송/cases/2026-meritz-damages/백서_나홀로전자소송×AI에이전트협업_[사건번호].md`로 저장.

**교재화 우선순위(박씨 지정)**: 백서 3장 "AI-인간 협업 원칙"(동석 필수 vs 무인 가능 구분표,
속도-학습 매칭 원칙, 플랫폼 제약 현실인식, 변호사 역할의 AI 대체범위)이 재사용 가치가 가장
높은 부분 — 교재 만들 때 **이 챕터부터** 작업 시작할 것. [[072-ecourt-ai-agent-workflow-2026-09-18]]
(개발일지, 같은 폴더에 있음)와 함께 원자료로 쓸 것.

**폴더명 관련 미결정 사항**: 박씨가 "`legal/ecourt-litigation/`(영문)으로 갈 수도 있다"고
언급함 — 현재는 `리걸/전자소송`(한글)로 이미 커밋됨. 리네임 여부는 박씨 확인 필요, 임의로 바꾸지 말 것.

related: [[project_architecture]] [[project_adb_sms_kakao_verification]]

## ✅ 2026-09-28 보정명령 대응 완료 — 보정서 접수 10:59

- 송달: 발송 09.17 / **수신 09.18** (전체송달문서에서 확인) → 마감 10.12였음. 접수번호 202609280002406583158
- 제출: 보정서(시스템 자동생성) + 첨부 법인등기사항전부증명서[제출용] 3쪽(09-21 발행, 폰 Quick Share 수신본을 ADB로 회수). 보정명령 파일은 미첨부
- 경로: 전체송달문서 → 보정명령등본 행 "관련서류 제출" → 보정서. 섹션별 "등록" 버튼 필수, 첨부는 "목록에 추가" 필수
- **screen-pilot MCP 는 이제 연결됨** (cmd.exe 풀패스로 수정됨). (0,0) fail-safe 주의 — 마우스 중앙 이동 후 클릭
- 캡처는 Windows python `SetProcessDpiAwareness(2)`+pyautogui.screenshot (PowerShell CopyFromScreen 은 DPI 150%에서 잘림)
- Chrome 다운로드 폴더 = `D:\UserFolders\Downloads`. 업로드 원본은 `C:\Temp\ecourt\`
- 상세 일지: `~/buckleychang.com/리걸/전자소송/073-bojeong-submission-2026-09-28.md`
- 다음: 피고 답변서/변론기일 통지 대기

## 2026-09-28 저장 구조 재편 + ecourt MCP (조회 전용)

- 🔴 **사건 자료 = `~/ecourt-private/` (로컬 git, remote 없음)** — buckleychang.com 은 private 레포지만 Pages 가 켜져 있어 소장·등본·증거가 buckleychang.com/리걸/... 로 공개 서빙되고 있었음(HTTP 200 실측). 4f40ec5 로 제거, 404 확인. 사건 자료를 Pages 켜진 레포에 절대 커밋 금지
- 체크리스트 스킬: `~/.claude/skills/ecourt-filing/SKILL.md` (절대 규칙: 서명·제출·결제·삭제 금지 등)
- 도구 코드: `~/buckleychang.com/tools/ecourt/` — MCP `ecourt` 등록(user scope): ecourt_status / ecourt_open_login / ecourt_service_list / ecourt_deadline. guard.py 가 금지 버튼 코드 차단
- 전용 Chrome: 포트 **9444**, 프로필 `C:\tmp\ecourt-cdp` (9222·9333 은 다른 자동화가 사용 중 — 건드리지 말 것). CDP 에서 공동인증서 창 정상 동작 확인. 첫 실행 시 "이 기기의 다른 앱 및 서비스에 액세스" 허용 필요
- 박씨 원칙: "두 번째로 같은 작업 할 때 도구로 해보고 고친다" — prepare_filing 은 2회차 제출 때 동석 시험 후 추가
- 미완: service_list 실데이터 파싱(로그인 후 1회 시험)

## 펜딩 (2026-09-28 세션 종료 시점)
- 전체 목록: `~/ecourt-private/PENDING.md` — 다음 세션 시작점
- 핵심: 답변서/기일 대기 · ecourt MCP reconnect 후 service_list 실데이터 시험(박씨 로그인 1회) · prepare_filing 은 2회차 동석 시험 · 다른 Pages 레포 개인정보 전수점검 · ~/ecourt-private 백업 위치 결정


## 2026-10-03 답변서 수신 + ecourt MCP 확장
- 피고 답변서부본(10-02자) 수신·열람(10-03 00:04). 주위적(접촉·인과 부인, 기왕손상) + 예비적(불법주차 20%) 정형문, 증거 없음, 기일·기한 통지 아직 없음. 박씨 결정: 청구 2,200,000 유지, 타이어 쟁점화 안 함, 합의 최저선 미정.
- 사건 요약·증거 맵·열린 질문: `~/ecourt-private/cases/2026-meritz-damages/KNOWLEDGE_사건요약_20261003.md` (준비서면 초안 v1 같은 폴더).
- ecourt MCP 도구 추가(코드 커밋 완료, **/mcp reconnect 필요**): open_service_doc(confirm_read)·interest·fault_table·case_notes. open_service_doc 실브라우저 경로는 **미시험**(로그인 필요).
- 무인 알림 불가(인증서·30분 세션) → Gmail scourt.go.kr 메일 감시로 대체 예정(미구현). 화해/이행권고결정 2주 이의기간 주의.
- 교훈: logged_in 오탐 수정, 갑6=피고차량 오인 정정, 외부 AI 분석은 원문 대조 후 사용.

- 2026-10-03 추가: 종합 사건평가서(6렌즈: 사건이론·입장vs이익·BATNA기대값·결정나무·판사심리·편향점검) = `11_사건평가서_20261003.md`, 일반 틀 = `tools/ecourt/ASSESSMENT.md`(수사학·스콜라·위그모어·협상학 등 학문 차용). 도구 `ecourt_expected_value`, case_notes topic assessment/framework. 확률·합의최저선은 박씨 입력 대기. 리걸 교재 소재로도 활용 가능.
- 2026-10-03 MCP 설계 원칙(박씨): 코드만이 아니라 **이야기·지식 텍스트도 MCP 안에** → resources(ecourt://guide/knowledge·assessment, ecourt://devlog/{074}, ecourt://case/{case}/{status|knowledge|assessment|brief|plan}) + prompts(blind_video_questions, hearing_rehearsal). 에이전트 대상 맥락 배포(START_HERE·AGENTS·journal 01~03 가린판·demo·selfcheck.py) 추가. 사건 자료·개발일지는 **로컬(~/ecourt-private)만**, 원격 없음(박씨 결정). 개발일지 074 작성. buckleychang.com 미푸시(Pages 공개 주의).

## 2026-10-03 ecourt v1.0.0 (태그 ecourt-v1.0.0, 로컬·미푸시)
- 법률 두뇌/브라우저(ECOURT_BROWSER)/사건저장소 분리, 도구 32, 로펌 12기능(firm.py), selfcheck 35·repro_test PASS, pre-push 차단 훅, D: git bundle 백업(post-commit). 상세 devlog 075.
- 실사건: 준비서면 초안 v2(독립 검토 1회차 FAIL 8건 반영). "피고가 접촉 인정"은 과장 → "다투지 않는 것으로 보인다"로 낮춤.
- 약관: 전자소송포털 제15조·제14조② — 자동화 명시 금지 없음, 영리·제3자 인증장치 사용 금지 → 브라우저 모듈 공개 배포 보류.

## 세션 종료 2026-10-03 (다음 시작점)
- 준비서면 초안 v6(독립 검토 4회 반영), 정보공개청구 문안(14_), 만19세 백서 v2(references/age19-open-strategy.md, ecourt://reference/age19).
- 박씨 대기: 타이어 처리 범위 / 앞바퀴 틀어진 이유·경사 / 경찰 접수 여부 / 구청 "지정 없음 vs 표지 없음"+정보공개청구 제출 / DB 출동내역서 / 사고 전 사진 / OC / 원격 백업·푸시 결정.
- buckleychang.com 미푸시(태그 ecourt-v1.0.0 로컬). /mcp reconnect 필요.
