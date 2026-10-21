# PC Eyes Final v2 — Windows GUI 눈 믹스 세트

**일자**: 2026-06-22 KST | **방법론**: W집합(v6) + 커뮤니티 메타 역산 | **레포**: `dtslib-localpc` / `C:\Users\dtsli\pc-eyes\`

---

## 1. 핵심 명제

"에이전트가 Windows GUI를 보려면, **웹 눈과 데스크톱 눈을 분리**하고, 데스크톱은 **UIA 정공 + Rust 속도 + 시각 fallback** 3단으로 쌓는다."

사람 감각이 본질인 구간(W1 30% / W2 극소수 / W4 장애)만 Windows 성역으로 남기고, 나머지는 에이전트가 대신 본다.

---

## 2. 최종 눈 믹스 세트 — 결정 점수평가

### 2.1 후보 풀 (커뮤니티 2026 전수조사)

| # | MCP 서버 | 언어 | 별 | UIA | Rust | 시각fallback | 토큰효율 |
|---|---|---|---|---|---|---|---|
| A | **desktop-touch-mcp** | Rust | ~1.5K⭐ | ★★★★★ | ★★★★★ | ★★★★★ (SoM OCR) | ★★★★★ (MPEG diff 60~80%) |
| B | Windows-MCP | Python | 4.7K⭐ | ★★★★ | ❌ | ★★★ (스크린샷) | ★★ |
| C | ScreenPilot | Python | ~40⭐ | ★★★ | ❌ | ★★★ (PyAutoGUI) | ★★ |
| D | UIA-X | Python | Trending | ★★★★ | ❌ | ★★★ | ★★ |
| E | Cua | Rust+Py | 16K⭐ | ★★★★ | ★★ | ★★★★ | ★★★ |
| F | terminator-mcp-agent | Rust | 1.5K⭐ | ★★★ | ★★★★ | ❌ | ★★★ |
| G | @playwright/mcp | JS | 28.9K⭐ | ❌ (web only) | ❌ | ★★★★ (vision auto) | ★★★★ |

### 2.2 W1(REAPER) 가중치 평가

| 기준 | 가중치 | A desk-touch | B Win-MCP | C ScreenPilot | D UIA-X | E Cua | F terminator | G Playwright |
|---|---|---|---|---|---|---|---|---|
| UIA 속도 | 35% | **10** (2ms) | 5 (Python) | 4 | 5 | 5 | 8 (Rust) | 0 |
| REAPER HWND 정밀도 | 25% | **10** (29 tools) | 7 | 6 | 7 | 6 | 6 | 0 |
| 설치 간편성 | 15% | **9** (npm 1줄) | **9** (pip 1줄) | 8 | 8 | 4 (QEMU) | 7 | **9** |
| W2 fallback | 10% | **10** (SoM OCR) | 6 | 6 | 6 | 7 | 4 | 6 |
| 토큰 절약 | 10% | **10** (60~80%) | 3 | 3 | 3 | 5 | 5 | 8 |
| 커뮤니티 검증 | 5% | 7 | **9** (4.7K) | 3 | 5 | **9** (16K) | 7 | **10** (28.9K) |
| **가중합** | 100% | **9.65** | 6.30 | 5.00 | 5.65 | 5.50 | 6.40 | 2.80 |

### 2.3 최종 선정

| 순위 | MCP | 점수 | 역할 | 가격 |
|---|---|---|---|---|
| **1순위** | **desktop-touch-mcp** | **9.65 / 10** | W1/W2 주력 눈 (Rust UIA + SoM) | MIT 무료 |
| Fallback | ScreenPilot | 5.00 | desktop-touch blind 시 백업 | MIT 무료 |
| 브릿지 | Playwright MCP | 2.80 | WSL 웹 작업 브릿지 (Windows에만 등록) | MIT 무료 |
| **Watch** | Cua | — | 샌드박스 필요 시 재평가 | MIT 무료 |

---

## 3. 개발 계획 — 3단계

### Phase 1: 설치 및 기초 검증 (오늘 완료)

```
□ C:\Users\dtsli\pc-eyes\               폴더 생성          ✅
□ PyAutoGUI 0.9.54                       pip 설치 확인      ✅
□ Pywinauto 0.6.9                        pip 설치 확인      ✅
□ ScreenPilot                            git clone + deps   ✅
□ Playwright 1.61.0 + Chromium           npm install + dl    ✅
□ dtslib-localpc docs/pc-eyes.md         연동 문서 생성     ✅
□ Telegram 전송                          PC_EYES_REPORT.md  ✅
□ desktop-touch-mcp 설치                 (설치 대기)        ⬜
```

### Phase 2: MCP 등록 및 W1 검증 (1시간)

```
1. desktop-touch-mcp 설치:
   npm install -g @harusame64/desktop-touch-mcp

2. MCP 등록 (settings.json):
   - desktop-touch (npm, 1순위)
   - screen-pilot (Python fallback)
   - playwright (web bridge)

3. W1 테스트 체크리스트:
   □ FX 창 감지: desktop-touch UIA 2ms
   □ Play+Record: 버튼 클릭 or WM_COMMAND 1013
   □ "OFELINE" 감지: SoM OCR → HASDATA 트리거
   □ WAV 완료 감시: sox RMS 자동판정
```

### Phase 3: W2/W4 확장 및 자동화 완성 (비정기)

```
W2:
  □ ExtendScript 첫 스크립트: "선택영역 PNG 200% export"
  □ desktop-touch SoM OCR: Adobe 버튼 탐색 테스트
  □ Tab S9 SuperDisplay USB 세팅 (W2 발동조건)

W4:
  □ KB5083769 대응 스크립트 패키징
  □ 복구 콘솔 OCR → Telegram 리포트 파이프라인
```

---

## 4. 아키텍처 최종도

```
                         ┌──────────────────┐
                         │   Claude Code    │ (MCP only)
                         └────────┬─────────┘
                                  │
                    ┌─────────────┼──────────────┐
                    │             │              │
              desktop-touch   ScreenPilot   Playwright
              (Rust UIA)     (Py fallback)  (web bridge)
              W1/W2 주력     W1/W2 보조     WSL 브릿지
                    │             │
                    ▼             ▼
              ┌──────────┐  ┌──────────┐
              │ W1 REAPER│  │ W2 Adobe │
              │ W4 콘솔  │  │ 커스텀UI │
              │ (UIA 정) │  │ (SoM 시) │
              └──────────┘  └──────────┘
```

**실행 원칙**:
1. 에이전트는 desktop-touch 먼저 호출 (UIA 되면 2ms)
2. UIA 실패 시 ScreenPilot fallback (PyAutoGUI 좌표/이미지)
3. 웹 필요 시 Playwright — Windows가 아닌 WSL에서 우선 처리
4. MCP 3개 모두 **로컬 전용 → 과금 0원**

---

## 5. 비용 정리

| 항목 | 금액 | 비고 |
|---|---|---|
| desktop-touch-mcp | **₩0** | MIT 오픈소스, 로컬 Rust 엔진 |
| ScreenPilot | **₩0** | MIT 오픈소스, 로컬 Python |
| Playwright MCP | **₩0** | MIT, 로컬 Chromium |
| PyAutoGUI/Pywinauto | **₩0** | BSD/MIT |
| Cua (추후) | **₩0** | 로컬 QEMU VM 자체운영 |
| **합계** | **₩0** | 외부 API·클라우드 종속 없음 |

---

*첨부: PC_EYES_WHITEPAPER_v2.md (상세 백서, 동일 폴더)*  
*이 문서: PC_EYES_FINAL_v2.md — 결정·점수·계획 1장 요약*
