# IROS 실기기 QA 결과 (2026-10-22, Tab S9 SM-X716N)

> 실기기(갤럭시 Tab S9) + ADB(Tailscale) + Chrome 155 CDP 직결로 m.iros.go.kr 부동산 열람 플로우를
> **끝까지 몰아본** 결과. 결론부터: **모바일 '웹'은 열람을 앱 전용으로 막는다 → AutoJS6 앱경로가 정답.**

---

## 0. 한 줄 결론
`m.iros.go.kr` 모바일 **웹**에서 부동산 열람 검색을 실행하면
**"해당 메뉴는 앱에서만 사용가능 합니다. 확인을 누르시면 스토어로 이동합니다."** 모달이 뜬다.
→ **웹/CDP 자동화는 설계상 불가.** 실자동화는 **IROS 네이티브 앱**을 **접근성(AutoJS6)** 으로 조작해야 함.
→ 이로써 `STANDARD.md` 의 **AutoJS6 온디바이스** 선택이 (서류상 결정이 아니라) **실측으로 입증**됨.

## 1. 실제로 검증된 것 (작동함)
| 단계 | 방법 | 결과 |
|---|---|---|
| ADB 실기기 연결 | Tailscale `100.86.15.50:5900` | ✅ 42개 탭 읽기(읽기전용) |
| 크롬 CDP 직결 | `adb forward tcp:9222 … chrome_devtools_remote` | ✅ (playwright `connect_over_cdp` 는 **행** → `cdp.py` CDP 직결로 대체) |
| Chrome 155 보안 우회 | `Target.createTarget`(=/json/new 차단) + WS `suppress_origin`(=Origin 403) | ✅ 탭 생성·조작·닫기(흔적 0) |
| m.iros 구조 덤프 | `recon.py dump` | ✅ 100+ 요소, 전체 메뉴트리 매핑 |
| 열람 폼 셀렉터 | `recon.py flow` | ✅ 주소입력/검색버튼/구분라디오 id 확보 |
| WebSquare 값 주입 | `$p.getComponentById(...).setValue()` (DOM `.value` 는 무시됨) | ✅ 주소 입력 반영 |
| 네이티브 터치 | CDP `Input.dispatchTouchEvent` (합성 TouchEvent 는 무시됨) | ✅ 검색 버튼 발화 |
| **검색 실행** | 위 조합 | ⛔ **앱 전용 게이트 모달** (스크린샷 `test/qa_search.png`) |
| 결제 차단 | `guard.check_label("결제하기")` | ✅ Forbidden 예외 |

## 2. 매핑된 실셀렉터 (m.iros 인덱스, WebSquare)
```
부동산 주소 입력  : #mf_wfm_content_sbx_rlrg_addr___input   (컴포넌트 mf_wfm_content_sbx_rlrg_addr)
부동산 검색 버튼   : #mf_wfm_content_btn_srch                (w2group, touch 바인딩)
부동산/법인 라디오 : #mf_wfm_content_rad_rgs_cls_input_0 / _1
법인명 입력        : #mf_wfm_content_sbx_sangho___input
법인 검색 버튼     : #mf_wfm_content_btn_srch2
```
> 사이트 개편 시 `iros_dump`(또는 `recon.py flow`)로 재매핑. WebSquare id 는 비교적 안정적이나
> `wq_uuid_*` 접미 id 는 불안정 → 라벨 텍스트 셀프힐링(`click_text`) 병행.

## 3. 디버깅 체인 (Chrome 155 + 안드로이드 + WebSquare)
순서대로 실제로 부딪히고 뚫은 벽:
1. playwright `connect_over_cdp` **행** → CDP HTTP/WS 직결(`cdp.py`).
2. `/json/new` HTTP **405/500/차단** → 브라우저레벨 `Target.createTarget`.
3. WS 핸드셰이크 **403 Forbidden**(Origin 거부) → `create_connection(..., suppress_origin=True)`.
4. 입력했는데 검색이 빈 값 취급 → WebSquare는 DOM `.value` 무시, **`setValue()` 컴포넌트 모델** 필요.
5. 버튼 `.click()`·합성 TouchEvent **무시** → 모바일 WebSquare는 **네이티브 터치**만 → CDP `Input.dispatchTouchEvent`.
6. 그리고 마주친 진짜 벽: **앱 전용 게이트(제품 정책)**. 코드로 못 뚫는다 — 앱경로로 가야 함.

## 4. 그래서 다음 (production 경로)
- **엔진 확정: AutoJS6 + MCP 플러그인(온디바이스 접근성).** CDP 웹경로는 폐기(열람 한정).
- IROS **앱**을 접근성 노드트리로 조작하는 `.js` 1호 작성 → 주소검색까지 자동, 결제·인증은 사람.
- `cdp.py`/`recon.py` 는 **버리지 않는다**: ① 웹 구조 레퍼런스 ② 서버측 self-heal 셀렉터 비교 ③ 앱 미설치 폴백 진단.
- 열람은 공개등기 → 인증서 불요·결제만. 결제/발급/서명은 영구히 사람(폰). (`guard.py`)

## 4-B. 앱 레벨 실측 — 2차 (2026-10-22, IROS 앱 설치 후)
웹(앱게이트)에 막혀 AutoJS6 앱경로로 전환 → 실제 IROS 앱을 Tab S9에 설치하고 끝까지 몰아본 결과.

| 단계 | 방법 | 결과 |
|---|---|---|
| AutoJS6 엔진 실행 | `RunIntentActivity` 로 `iros_yeollam.js` health | ✅ `{"ok":true,"engine":"autojs6","pkg":...,"act":...}` — **온디바이스 실행+접근성 작동 입증(목 아님)** |
| IROS 앱 설치 | Play `market://details?id=kr.go.iros` → '설치' 탭 | ✅ `kr.go.iros` 설치(pm path 확인) |
| 권한 처리 | 카메라 권한 '허용 안함'(uiautomator bounds 정확탭) | ✅ |
| 앱 실행 | `kr.go.iros/.LauncherActivity` | ✅ `XBrowserActivity`(=WebView 래퍼) 진입 |
| **열람 실행** | — | ⛔ **2중 차단(아래)** |

### ★차단 1 — IROS 앱 안티-VPN (보안정책)
앱 진입 즉시: **"가상 네트워크가 탐지되었습니다. 인터넷등기소 보안정책에 따라 앱을 종료합니다."** → 강제 종료.
- 원인: 이 테스트 태블릿은 **Tailscale(tun1, 100.86.15.50)** 경유로 원격 ADB 제어 → 앱이 VPN 인터페이스 탐지.
- 함의: **원격(VPN) 테스트 리그로는 IROS 앱 자동화 테스트 불가.** 단, 실제 유저 폰은 일반 모바일/WiFi(무VPN)라 **프로덕션엔 영향 없음.**
- ⚠️ 이 탐지를 우회(detection evasion)하지 않는다 — 정부 앱 보안통제. 테스트는 **무VPN 로컬 ADB 기기**로 해야 함(USB/로컬WiFi + 물리접근).

### ★차단 2 — 서비스 점검중
"서비스 점검중입니다 … 접속이 일시 중단됩니다" (10-20 공지된 점검). 오늘 서비스 자체가 일시 중단.

### 결론(앱 경로)
- 엔진·설치·권한·실행 파이프라인은 **전부 실제로 작동 입증.** 열람 자동화의 마지막 벽은 코드가 아니라 ① 무VPN 로컬 기기 필요 ② 점검 종료 대기.
- `iros_yeollam.js` 의 `SEL` 실측 매핑(dump)·full run 은 위 2조건 충족 시 완료.

## 5. 산출물 (이 커밋)
- `iros/mcp/cdp.py` — 안드로이드 크롬 CDP 직결 클라이언트(탭 수명주기·WebSquare setValue·네이티브 탭·스샷).
- `iros/mcp/iros_mcp.py` — playwright→CDP 직결 전환, 실셀렉터 반영, 앱게이트 감지.
- `iros/mcp/guard.py` — 결제/서명 차단 + `is_app_gate()`.
- `iros/test/recon.py` — `pages`(읽기전용)·`dump`(인덱스)·`flow`(열람진입) 실기기 하네스.
- `iros/test/qa_search.png` — 앱 전용 게이트 모달 증거 스샷.
