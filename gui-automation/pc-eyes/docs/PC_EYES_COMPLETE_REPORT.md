# PC Eyes Complete Report — Windows GUI 시각 자동화

**일자**: 2026-06-22 KST | **방법론**: W집합(v6) + 커뮤니티 메타 역산 | **레포**: dtslib-localpc / C:\Users\dtsli\pc-eyes\

---

## 1. 문제 정의

"상용 프로그램은 AI가 만든 것보다 퀄리티가 높다. 그러면 그걸 버리지 말고, AI로 감싸서 쓰면 된다."
Claude Code가 Windows GUI(W1 REAPER, W2 Adobe, W4 OS 기반)를 보고 조작할 수 있어야 한다.
웹은 WSL 본진에 맡기고, Windows 성역은 Windows 전용 도구로만 채운다.

## 2. 설치 현황 (C: 드라이브)

| 도구 | 버전 | 역할 | 상태 |
|---|---|---|---|
| desktop-touch-mcp | 1.10.4 | Rust UIA 주력 (29 tools, SoM OCR, MPEG diff) | ✅ npm global |
| ScreenPilot | git main | Python FastMCP fallback | ✅ git clone + pip |
| Playwright | 1.61.0 | 웹 헤드리스 브라우저 | ✅ npm global |
| PyAutoGUI | 0.9.54 | Python 스크린샷/마우스 | ✅ pip |
| Pywinauto | 0.6.9 | UIA 백엔드 | ✅ pip |
| @playwright/mcp | 0.0.68 | MCP 서버 (웹 브리지) | ✅ npm global |

**설치 비용: ₩0 (전체 MIT 오픈소스, 로컬 전용, 외부 API 종속 없음)**

## 3. 아키텍처

```
                        ┌──────────────────┐
                        │   MCP Layer     │
                        │  (Claude Code)  │
                        └────────┬─────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
        desktop-touch       ScreenPilot        Playwright
        (Rust UIA)          (Python)           (JS)
        W1/W2 주력          UIA blind fallback  WSL 브릿지
       ┌──────────┐       ┌──────────┐       ┌──────────┐
       │ REAPER   │       │ Adobe    │       │ Web      │
       │ Win32    │       │ CustomUI │       │ Headless │
       │ UIA 정공 │       │ SoM OCR  │       │ DOM 기반  │
       └──────────┘       └──────────┘       └──────────┘
```

## 4. MCP 등록 (settings.json) — 3개 PC Eyes 전용

| MCP | 명령어 | 역할 |
|---|---|---|
| desktop-touch | `npx @harusame64/desktop-touch-mcp` | 29개 GUI 툴 (Rust UIA 2ms) |
| screen-pilot | `python ScreenPilot/main.py` | Python fallback |
| playwright | `node @playwright/mcp/cli.js` | 웹 자동화 |

## 5. 프로젝트 구조

```
C:\Users\dtsli\pc-eyes\
├── README.md
├── docs/
│   ├── PC_EYES_REPORT.md          ← v1 설치 보고서
│   ├── PC_EYES_WHITEPAPER_v2.md   ← v2 상세 백서 (10장)
│   ├── PC_EYES_FINAL_v2.md        ← 결정+점수+계획 1장
│   └── PC_EYES_COMPLETE_REPORT.md ← 본 문서 (종합)
├── scripts/
│   ├── test_all_layers.py         ← 통합 테스트
│   ├── watchdog.ps1               ← Windows CC 헬스체크
│   ├── pc-eyes-wsl-banner.sh      ← WSL SSH 배너
│   ├── termux-widget-wrapper.sh   ← 폰 위젯 래퍼
│   ├── deploy-all.sh              ← 전체 배포 스크립트
│   ├── start_reaper.ps1           ← REAPER 기동+대기
│   ├── enum_windows.ps1           ← 창 열거 유틸
│   ├── find_reaper.ps1            ← REAPER 창 찾기
│   ├── find_reaper_v2.ps1         ← REAPER 창 찾기 v2
│   └── dismiss_reaper_dialogs.ps1 ← 시작 다이얼로그 처리
├── tests/
│   ├── ss_playwright.png          ← Playwright 헤드리스 스크린샷 (53KB)
│   └── ss_pyautogui.png           ← PyAutoGUI (대화형 세션 필요)
├── logs/
│   └── test_report.txt            ← 4계층 통합 테스트 로그
└── ScreenPilot/                   ← MCP GUI 서버 (git clone)
    ├── main.py + core/
    └── requirements.txt
```

## 6. 강제 리마인더 시스템 (3계층)

| 계층 | 위치 | 실행 방식 | 상태 |
|---|---|---|---|
| L1 Termux 위젯 | 폰 ~/.shortcuts/ | 위젯 터치 시 헬스체크 후 WSL 접속 | 📄 스크립트 준비, scp 배포 필요 |
| L2 WSL SSH 배너 | WSL ~/.bashrc | SSH 로그인 시 자동 출력 | ✅ 설치 완료 |
| L3 Windows Watchdog | watchdog.ps1 | 수동 실행 (PowerShell) | ✅ 스크립트 준비 |

## 7. 결정 점수평가 (선정 사유)

**가중치**: UIA 속도 35% | REAPER 정밀도 25% | 설치 간편성 15% | W2 fallback 10% | 토큰 절약 10% | 커뮤니티 검증 5%

| 순위 | 도구 | 점수 | 이유 |
|---|---|---|---|
| 🥇 | desktop-touch-mcp | **9.65/10** | Rust UIA 2ms, 29 tools, SoM OCR, MPEG diff |
| 🥈 | terminator-mcp-agent | 6.40 | Rust but no visual fallback |
| 🥉 | Windows-MCP | 6.30 | 4.7K⭐ but Python UIA slow |
| 4 | UIA-X | 5.65 | Cross-platform but immature |
| 5 | Cua | 5.50 | 16K⭐ but QEMU VM overkill |
| 6 | ScreenPilot | 5.00 | Fallback only |
| 7 | Playwright MCP | 2.80 | Web only (WSL 영역) |

## 8. 현재 상태 평가 — "설치는 잘됐다. 운영 검증은 안 됐다."

### ✅ 완료: 설치/구조 (Phase 0)
- [x] desktop-touch-mcp npm 설치 완료 (Rust UIA 2ms)
- [x] ScreenPilot git clone + pip 설치 완료
- [x] Playwright + MCP 설치 완료
- [x] PyAutoGUI/Pywinauto 설치 완료
- [x] MCP 3개 settings.json 등록 완료
- [x] 프로젝트 디렉토리 구조 완성 (docs/scripts/tests/logs)
- [x] 3계층 리마인더 시스템 스크립트 완성
- [x] 비용 ₩0 (전체 오픈소스 MIT)

### ❌ 미완료: 운영 검증 (Phase 1)
- [ ] W1 REAPER: FX 창 UIA 감지 → Play+Record 자동화 (다이얼로그 처리까지 필요)
- [ ] W1 OFELINE 감지: SoM OCR → HASDATA 트리거
- [ ] W1 WAV 완료 감시: sox RMS 자동판정
- [ ] W2 Adobe: desktop-touch SoM OCR 버튼 탐색
- [ ] MCP 툴 Claude Code에서 실제 호출 테스트

### ⏳ 보류: 확장 작업 (Phase 2/3)
- [ ] Cua 샌드박스 재평가 (조건부)
- [ ] ExtendScript JSX 자동화 (Adobe 반복작업)
- [ ] 폰 위젯 scp 배포

## 9. 다음 행동 (1순위)

**W1 REAPER 단일 시나리오 완주**가 최우선. "눈이 진짜 일을 한다"는 로그를 하나 만드는 것.
REAPER 시작 → Replace missing file 다이얼로그 처리 → FX 창 확인 → Play+Record → WAV 감시 → sox RMS 판정

```
powershell 기반 창 제어 스크립트는 이미 준비됨:
  start_reaper.ps1           ← REAPER 실행 + 대기
  find_reaper_v2.ps1         ← EnumWindows로 창 탐색
  dismiss_reaper_dialogs.ps1 ← 시작 다이얼로그 처리 (WM_COMMAND/SendMessage)
```

---

*보고: 2026-06-22 KST | dtslib-localpc/pc-eyes*
*생성: Claude Code × PARKSY CTO 공동작업*
