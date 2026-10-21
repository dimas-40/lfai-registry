# PC Eyes — Windows 시각 GUI 자동화 스택

**설치일**: 2026-06-22 | **방법론**: W집합(v6) | **비용**: ₩0 (전체 MIT)

## 프로젝트 위치

| 환경 | 경로 |
|------|------|
| Windows C: (원본) | `C:\Users\dtsli\pc-eyes\` |
| **레포 (통합)** | **`D:\PARKSY\dtslib-localpc\pc-eyes\`** |
| WSL 접근 | `/mnt/d/PARKSY/dtslib-localpc/pc-eyes/` |

## 최종 선정

| 순위 | 도구 | 점수 | 역할 |
|------|------|------|------|
| 1순위 | desktop-touch-mcp (Rust) | 9.65/10 | W1/W2 주력 UIA 눈 |
| Fallback | ScreenPilot (Python) | — | UIA blind 시 backup |
| 브릿지 | Playwright MCP | — | WSL 웹 작업 |

## 주요 파일

- `docs/PC_EYES_COMPLETE_REPORT.md` — 종합 보고서 (선정/설치/상태/다음단계)
- `scripts/deploy-all.sh` — 3계층 리마인더 시스템 배포
- `scripts/watchdog.ps1` — Windows CC 헬스체크
- `scripts/pc-eyes-wsl-banner.sh` — WSL SSH 로그인 배너
- `scripts/test_all_layers.py` — 4계층 통합 테스트
- `ScreenPilot/` — FastMCP GUI 서버 (git clone)
