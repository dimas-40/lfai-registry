# ecfs.scourt.go.kr GUI 좌표/절차 기록 (1280x720, 2026-09-16 실측)

> PC(DTSLIB) 해상도 1280x720 기준. 해상도 바뀌면 전부 재실측 필요.
> 자동화 방식: `ecfs_pyauto.py` (pyautogui, Windows Python) — win32 mouse_event/SendKeys/SendInput는 작동 안 함(확정, 재시도 금지).

## 스크린샷 캡처 (WSL → Windows)

```bash
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Windows.Forms,System.Drawing
\$screens = [System.Windows.Forms.Screen]::AllScreens
\$bounds = [System.Drawing.Rectangle]::Empty
foreach (\$s in \$screens) { \$bounds = [System.Drawing.Rectangle]::Union(\$bounds, \$s.Bounds) }
\$bmp = New-Object System.Drawing.Bitmap \$bounds.Width, \$bounds.Height
\$g = [System.Drawing.Graphics]::FromImage(\$bmp)
\$g.CopyFromScreen(\$bounds.Location, [System.Drawing.Point]::Empty, \$bounds.Size)
\$bmp.Save('C:\Temp\pc_screen.png', [System.Drawing.Imaging.ImageFormat]::Png)
"
cp /mnt/c/Temp/pc_screen.png <scratchpad>/pc_screen.png
# 그다음 Read 툴로 읽기
```

## GUI 조작 (WSL → Windows python.exe, pyautogui)

```bash
PYTHON="/mnt/c/Users/dtsli/AppData/Local/Programs/Python/Python312/python.exe"
cp ~/dtslib-papyrus/mcp-ecourt/tools/ecfs_pyauto.py /mnt/c/Temp/ecfs_pyauto.py
"$PYTHON" -c "
import sys; sys.path.insert(0, r'C:\Temp')
from ecfs_pyauto import *
click(900, 580)
paste_korean_text(900, 580, '텍스트내용')
"
```

## 로그인 후 메인 화면 (나의전자소송, PSP133M01)

- 로그인 방식: 신협 개인뱅킹 탭에서 인증서 로그인 → 전자소송 연동 (박씨 직접 수행)
- "서류제출" 메뉴 클릭 → 소장 작성 진입

## 민사서류-소장-1.문서작성 화면 (PSPA13M01)

좌측 사이드바 탭 (페이지 맨 위 상태, x=113 고정):

| 탭 | y좌표 |
|---|---|
| 사건기본정보 | 477 |
| 당사자 | 536 |
| 법정대리인 | 595 |
| 청구취지 | 655 |
| 청구원인 | 712 |
| 입증서류 | (스크롤 필요, 미확정) |
| 첨부서류 | (스크롤 필요, 미확정) |

**중요**: 사이드바가 페이지와 함께 스크롤되므로, 탭 클릭 전 반드시 페이지를 맨 위로
올려야 위 좌표가 유효함. 안 그러면 엉뚱한 곳 클릭됨 (실제로 09-16 세션에서
당사자 등록 화면인 줄 알고 열어보니 나의사건현황이었던 사고 발생 — 사이드바 좌표
믿고 스크롤 상태 확인 안 하면 오작동함).

### 사건기본정보 섹션

- 사건명 드롭다운: 클릭 후 "손해배상(자)" 선택 (자동차사고 손해배상 전용 코드)
- 법원: 사고발생지/피고소재지 중 선택 (본 건은 [관할 법원] — 사고발생지 관할)
- 청구구분: 재산권상청구 (라디오, 금전청구는 항상 이거)
- 소가구분: 금액 (라디오)
- 소가: 숫자만 입력 (쉼표 자동 포맷)

### 당사자 섹션

- 당사자구분: 원고/피고 라디오 (원고 등록 시 자동으로 본인정보 프리필됨 — "내정보가져오기")
- 주민등록번호: 뒷자리는 민감정보라 **박씨 직접 입력** (Claude가 자동 타이핑 안 함, 정책)
- 송달영수인 아이디: 원고 본인(대리인 없는 소송)의 전자소송 로그인 아이디를 입력하고
  "사용자아이디확인" 버튼 클릭 — 비워두면 "송달영수인 ID를 확인해 주십시오" 알림 뜸

### 청구취지 (plain textarea)

- 붙여넣기 방식만 작동 (한글은 pyautogui.typewrite 불가 — 반드시 클립보드+Ctrl+V)
- 한글 2,000자 이내 제한
- 실무 원칙: 청구취지는 짧고 정확한 주문 형태 유지 (판결 구하는 내용만, 논증은 청구원인에서)

### 청구원인 (리치텍스트 에디터, CKEditor류)

- 한글 2,000자 이내 제한
- "직접입력" / "요건사실" 두 모드 중 직접입력 사용
- 파일첨부(내용파일첨부)로 HWP/DOC/PDF 등 첨부 가능 — 텍스트 대신 파일로 낼 수도 있음

### 입증서류

- 파일 업로드형 서증 목록 (갑 제1호증 등)
- **증거파일(사진/블랙박스/CCTV 등)이 아직 없으면 비워두고 진행 가능** — 전자소송은
  소장 접수 후 증거서류를 별도 추후제출서면으로 낼 수 있음 (2026-09-16 확인)

### 첨부서류

- 소장부본 등 시스템 자동 요구 체크리스트 — 별도 파일 업로드 불필요한 경우多

## 진단 기록 — 왜 win32 API 직접호출이 안 되는가

- `GetForegroundWindow()` → 정확히 Chrome 창 타이틀 반환됨
- `WindowFromPoint(900,580)` → "Chrome Legacy Window" 핸들 정상 반환됨
- 그런데도 `mouse_event`/`SendKeys`/`SendInput`(KEYEVENTF_UNICODE 포함) 전부 무反응
- ASCII "TEST123", 한글 "가" 전부 시도했지만 반영 안 됨 — 페이지가 스페이스바에는
  반응(스크롤)해서 키 자체는 전달되는데, 클릭이 실제 입력 필드에 포커스를 못 준 것으로 추정
- **pyautogui.click() + pyautogui.hotkey()는 정상 작동** — 내부적으로 다른 이벤트 생성 경로를
  타는 것으로 보임 (원인 미상이나 재현 확인됨). 앞으로는 무조건 pyautogui 경로만 사용.
