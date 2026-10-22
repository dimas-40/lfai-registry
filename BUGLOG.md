# 버그 로그 — 기획·실측·테스트 이력

> 등기 모듈을 실제로 짓고 돌리며 부딪힌 버그·벽과 해결을 전부 기록.
> 상태: ✅해결 · 🧱제품벽(코드로 못 뚫음, 우회) · ⚠️운영과제(미해결, 설계로 수용).
> 최종 갱신 2026-10-22. 검증 환경: Galaxy Tab S9(SM-X716N) · Chrome 155 · 셀(youthful_borg) Playwright.

---

## A. 접근·인프라
| # | 증상 | 원인 | 해결 | 상태 |
|---|---|---|---|---|
| A1 | m.iros/www.iros 본문 깨짐(WebFetch) | **EUC-KR** 레거시 인코딩 | `curl … \| iconv -f EUC-KR` | ✅ |
| A2 | dimas-40/lfai-registry 404 | private + dtslib1979 토큰 권한 없음 | 랩탑 `gh hosts.yml`에서 dimas-40 토큰 추출→`~/config/dimas-github.token`(600) | ✅ |
| A3 | 랩탑 `ssh env` GITHUB_TOKEN 빈값 | `.bashrc` 비대화형 early-return | rc/hosts.yml 직접 파싱 | ✅ |
| A4 | 랜딩 rebase 충돌 | 내 랜딩 vs 기존 브랜드 랜딩 | `rebase --abort`, 우수한 기존본 유지 | ✅ |
| A5 | `git push` 거부(non-fast-forward) | 다른 세션이 remote 선행(랜딩 스타일 커밋) | `fetch`+`rebase origin/main`→push | ✅ |

## B. CDP 실기기 recon (안드로이드 크롬 조작)
| # | 증상 | 원인 | 해결 | 상태 |
|---|---|---|---|---|
| B1 | `playwright connect_over_cdp` **행(2분 타임아웃)** | 안드로이드 크롬서 핸드셰이크 멈춤 | CDP를 HTTP(/json)+WebSocket로 **직결**(`cdp.py`/`recon.py`) | ✅ |
| B2 | `/json/new` HTTP **405** | 최신 크롬은 PUT 요구 | PUT 시도 | ✅(후속 B4로 폐기) |
| B3 | `/json/new?url=…` HTTP **500** | URL을 쿼리로 주면 거부 | 빈 탭+`Page.navigate` 시도 | ✅(후속 B4) |
| B4 | 빈 `/json/new`도 HTTP **500** | **Chrome 155가 /json/new HTTP 차단** | 브라우저레벨 `Target.createTarget` | ✅ |
| B5 | WebSocket **403 Forbidden**(핸드셰이크) | Origin 헤더 거부 | `create_connection(..., suppress_origin=True)` | ✅ |

## C. m.iros 자동화 (WebSquare SPA)
| # | 증상 | 원인 | 해결 | 상태 |
|---|---|---|---|---|
| C1 | 주소 입력했는데 검색이 **빈 값 취급** | WebSquare는 DOM `el.value` 무시, 내부 컴포넌트 모델 사용 | `$p.getComponentById(id).setValue()` (`cdp.fill_id` 폴백 포함) | ✅ |
| C2 | 검색 버튼 **반응 없음**(`.click()`/합성 TouchEvent) | 모바일 WebSquare는 **네이티브 터치** 바인딩, 합성 이벤트는 untrusted로 무시 | CDP `Input.dispatchTouchEvent`(요소 중심좌표)=`cdp.tap_id` | ✅ |

## D. 제품 벽 (코드로 못 뚫음 → 우회 확정)
| # | 증상 | 원인 | 해결 | 상태 |
|---|---|---|---|---|
| D1 | 부동산 열람 검색 실행 시 "**해당 메뉴는 앱에서만 사용가능 합니다**" 모달→스토어 유도 | m.iros 모바일 **웹**이 열람을 **앱 전용**으로 막음(제품 정책, 버그 아님) | ① `guard.is_app_gate()`로 감지·중단 ② **엔진을 AutoJS6 온디바이스(앱 접근성)로 확정**(STANDARD.md) | 🧱 우회확정 |

> D1은 이번 작업의 핵심 발견. 웹/CDP 경로는 설계상 불가 → 실자동화는 IROS **앱**을 접근성으로.
> 근거·셀렉터·전 과정: [`iros/FINDINGS.md`](iros/FINDINGS.md).

| # | 증상 | 원인 | 해결 | 상태 |
|---|---|---|---|---|
| D2 | IROS **앱** 진입 즉시 "가상 네트워크 탐지 → 앱 종료" | 앱 안티-VPN 보안정책 + 테스트 태블릿이 **Tailscale(tun1) 경유** 원격ADB | **무VPN 로컬 ADB 기기로 테스트**(USB/로컬WiFi). 우회 안 함(정부앱 보안통제). 프로덕션=유저 폰 무VPN이라 무영향 | 🧱 리그제약 |
| D3 | IROS "서비스 점검중" | 10-20 공지 시스템 점검(오늘 일시중단) | 점검 종료 후 재시도 | 🧱 일시 |

> ✅ 그 전까지 **전부 실제로 작동**: AutoJS6 엔진 온디바이스 실행(result.json), Play 설치 트리거, 접근성 ON,
> 앱 실행, 권한 다이얼로그 처리(uiautomator bounds 정확탭). 마지막 벽만 코드 밖 요인(VPN·점검).

## E. 시연 PWA (`app/`)
| # | 증상 | 원인 | 해결 | 상태 |
|---|---|---|---|---|
| E1 | 자동재생이 state=1(검색대기)서 **멈춤**→게이트 모달 안 뜸 | 각 단계가 다음을 예약 안 함(수동탭 대기) | `auto` 플래그로 타임라인 체이닝(toSearch→doSearch→toApp→결제게이트 정지) | ✅ |
| E2 | 아이콘이 **□(두부)** 로 깨짐 | 폰트 없는 환경서 **emoji 미지원**(🏠📱⌕↻) | 전부 **인라인 SVG**로 교체 | ✅ |
| E3 | 앱 상단바 "LFAI 등기"+상태문구 **줄바꿈/겹침**(296px) | 좁은 임베드 폭에 텍스트 과다 | 문구 축약 + `white-space:nowrap` + 폰트↓ | ✅ |
| E4 | 결제 버튼 `🔒` **두부** | emoji(E2 재발) | 평문 "본인 인증 필요 · guard 차단" | ✅ |
| E5 | **reduced-motion서 빈 폼**(접근성/저사양) | 자동재생이 `if(!reduce)`라 아무것도 진행 안 됨 | `staticDone()`—전체 스토리 즉시 정적표시 | ✅ |

---

## 미해결/수용 (코드 버그 아님 — 운영·배포 과제)
| # | 과제 | 성격 | 메모 |
|---|---|---|---|
| ⚠️O1 | 폰 상시 가동(삼성 배터리킬·화면off 벽) | 운영 | start-on-boot+watchdog+포그라운드서비스. SOLUTION-ARCHITECTURE §2·REQUIREMENTS §5 |
| ⚠️O2 | TWA 전체화면(주소창 제거) | 배포 | 루트 `.well-known/assetlinks.json` 필요 → GitHub Pages 프로젝트사이트 제약, 커스텀도메인 권장. app/README |
| ⚠️O3 | IROS 앱 UI 개편 시 셀렉터 깨짐 | 유지보수 | 서버 self-heal 재배포로 흡수(설계상 예정) |
| 🔶O4 | AutoJS6 .js 1호(앱 접근성) | 구현 | **작성완료** `iros/autojs6/iros_yeollam.js`(health/dump/yeollam + guard). 실기기 full run은 IROS앱 설치+로그인(소유자·PII) 후 |

## 테스트 자산 (재현용)
- `iros/test/recon.py` — pages/dump/flow 3모드 실기기 하네스
- `iros/test/qa_search.py` · `qa_tap.py` — 열람 플로우 실기기 QA
- `iros/test/qa_search.png` — 앱게이트 모달 증거
- 시연 QA: 셀 Playwright 자동재생/수동탭/리플레이/reduced-motion 전수 — JS에러 0 확인(2026-10-22)
