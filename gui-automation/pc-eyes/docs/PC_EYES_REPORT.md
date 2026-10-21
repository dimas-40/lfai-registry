# 👁️ PC Eyes — Windows 시각 GUI 자동화 스택

**프로젝트**: `C:\Users\dtsli\pc-eyes\`  
**연동 레포**: `D:\PARKSY\dtslib-localpc\pc-eyes\`  
**설치일**: 2026-06-22  
**목적**: Claude Code가 Windows 환경에서 "눈"을 갖고 웹/데스크톱 GUI를 보고 제어

---

## 설치 현황

| 계층 | 도구 | 버전 | 상태 | 용도 |
|------|------|------|------|------|
| **L1** 웹 브라우저 | Playwright | 1.61.0 | ✅ | 웹 DOM 기반 자동화 + 헤드리스 스크린샷 |
| **L2** 데스크톱 GUI | PyAutoGUI | 0.9.54 | ✅ | 마우스/키보드/스크린샷 (대화형 세션 필요) |
| **L3** Win 컨트롤 | Pywinauto | 0.6.9 | ✅ | UI Automation API — 창/버튼/텍스트 직접 제어 |
| **L4** MCP 통합 | ScreenPilot | git main | ✅ | FastMCP 기반 GUI 제어 서버 (Claude MCP 직접연결) |

---

## 계층별 동작 요약

### L1 — Playwright (웹 눈)
- `chromium.headless: true` → 구글 페이지 열고 스크린샷 저장 ✅
- `@playwright/mcp` 0.0.68 글로벌 설치 완료 → MCP로 Claude 직접 호출 가능
- Chromium / Firefox / WebKit 모두 설치 가능
- **한계**: 웹 브라우저 내부만 볼 수 있음. 어도비/한글/탐색기 불가

### L2 — PyAutoGUI (데스크톱 눈)
- 스크린샷 / 마우스 이동 / 클릭 / 키보드 입력
- **⚠️ MSYS2 세션**: 비대화형 세선이라 screen grab 불가
- **해결법**: 실제 Windows 대화형 세션에서 실행 시 정상 작동
- `screen size: 1024x768` — 원격 세션 해상도 (실제 모니터와 다름)

### L3 — Pywinauto (Win 컨트롤 눈)
- UIA (UI Automation) 백엔드 기반 — 접근성 트리로 컨트롤 탐색
- 윈도우 핸들 / AutomationId / Name 기반 정밀 타겟팅
- 좌표 깨짐 없음 — 해상도 무관하게 동일 컨트롤 찾음
- **⚠️ 현재 세션**: visible windows = 0 (데스크톱 세션 없음)

### L4 — ScreenPilot (MCP 통합 눈)
- FastMCP 서버 (Python) — Claude와 직접 MCP 프로토콜 통신
- 6개 모듈: ScreenCapture / Mouse / Keyboard / Scroll / Element / ActionSequence
- `pip install -r requirements.txt` 완료, import 정상 ✅
- **Claude Desktop MCP config 에 등록하면 Claude가 직접 화면 제어 가능**

---

## 아키텍처 결정

```
                    ┌──────────────┐
                    │   Claude     │
                    │  (이 에이전트) │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        MCP Playwright  ScreenPilot   PowerShell
        (웹 브라우저)    (GUI 제어)    (직접 명령)
              │            │
              ▼            ▼
         Headless       UIA API +
         Chromium       PyAutoGUI
                        fallback
```

### 핵심: 두 가지 실행 모드

| 모드 | 설명 | 언제 쓰나 |
|------|------|-----------|
| **MCP 모드** | Claude가 직접 ScreenPilot/Playwright MCP 호출 | 에이전트 작업 중 GUI 필요할 때 |
| **직접 실행** | PowerShell → Python 스크립트 | 테스트/디버깅/단발성 작업 |

---

## 필요한 추가 작업

1. **ScreenPilot MCP 등록** — Claude Desktop settings.json 에 `screen-pilot` MCP 서버 추가
2. **MSYS2 세션 우회** — PyAutoGUI 스크린샷이 MSYS2에서 안 되므로, 별도 Windows 에이전트(Windows CC 세션)에서 직접 실행하는 구조 필요  
   → 해법: Windows CC 세션(이 세션)이 PowerShell 직접 호출, ScreenPilot MCP가 대화형 세션에서 실행
3. **썸네일: dtslib-localpc 연동** — pc-eyes/README.md 를 dtslib-localpc/docs/ 에 복사

---

## Playwright 구동 테스트 결과

```
PAGE TITLE: Google
SCREENSHOT SAVED — C:\pc-eyes\tests\ss_playwright.png (53KB)
PLAYWRIGHT FULL TEST OK
```

---

## 설치 명령어 요약

```powershell
# Playwright (npm 전역 — 이미 설치됨)
npm install -g playwright @playwright/mcp
npx playwright install chromium

# Python 데스크톱 도구 (pip — 이미 설치됨)
pip install pyautogui pywinauto pillow

# ScreenPilot (git clone + pip)
git clone https://github.com/Mtehabsim/ScreenPilot.git
pip install -r ScreenPilot/requirements.txt
```

---

*보고: 2026-06-22 17:20 KST | dtslib-localpc/pc-eyes*
