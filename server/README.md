# LFAI 등기 — 쿠폰 백엔드 (실서버)

> `coupon_server.py` — ADB 연결 쿠폰 발급·검증·원자적 사용처리. **의존성 0**(파이썬 표준 + sqlite3).
> 연산/용량 거의 0 — "GPU·무거운 서버 불필요"([`../REQUIREMENTS.md`](../REQUIREMENTS.md))를 그대로 증명.

## 실행
```bash
python3 server/coupon_server.py        # 기본 :8787, DB=~/lfai-coupon-data/coupons.db
LFAI_COUPON_PORT=8787 python3 server/coupon_server.py
```

## API (JSON)
| 메서드 | 경로 | 바디 | 응답 |
|---|---|---|---|
| GET | `/health` | — | `{ok,service,version}` |
| POST | `/api/coupon/issue` | `{tier}` | `{ok,code,tier,uses,status,expires}` |
| POST | `/api/coupon/validate` | `{code}` | `{ok,valid,status,remaining}` |
| POST | `/api/coupon/redeem` | `{code}` | `{ok,session_id,remaining}` (1회 원자적 차감) |
| POST | `/api/session/run` | `{code,address}` | 쿠폰 소진 후 **실기기 ADB 세션 구동**(adb_runner) → `{ok,stage,search,url,...}` |
| GET | `/api/stats` | — | `{issued,redeemed}` (PII 없음) |

### /api/session/run — 쿠폰→실기기 ADB 자동구동
`adb_runner.py` 가 폰 크롬을 CDP로 잡아 m.iros 부동산 열람 플로우 구동:
`adb connect/forward → m.iros 탭 → 부동산 선택 → 주소 setValue → 검색(WebSquare comp.click) → 결과판정 → 탭닫기`.
- 쿠폰은 **기기 구동 전 원자적 소진**(재사용 차단). `address`=PII는 서버 저장 안 함(길이만).
- 반환 `stage`: `searched`(검색완료) / `app_gate`(웹 열람 앱전용 → AutoJS6 경로) / `payment_gate`(결제=사람) / `maintenance` / `no_device`.
- 환경변수: `IROS_DEVICE`(기본 Tab S9 Tailscale), `IROS_CDP_PORT`(9222).
- ⚠️ 이 엔드포인트는 **서버에 연결된 기기**를 구동 — 프로덕션에선 각 유저 폰(무선ADB 페어링)으로 바인딩.

- 티어: `TRIAL`(무료·1회·24h, 즉시활성) · `R1`(3000원·1회·72h) · `R10`(25000원·10회·720h).
- 유료는 `status=pending_payment` → **PG 연동 전엔 redeem 차단**(정직). 결제 붙으면 active 전환.
- 보안: eval/경로접근 없음 · CORS 화이트리스트(`dimas-40.github.io`) · IP당 60rpm 레이트리밋 · PII·IP 로그 안 남김.
- 이중사용 방지: `UPDATE … WHERE uses>0` rowcount 검사(원자적).

## 공개 노출 (Tailscale Funnel)
프런트(GitHub Pages)가 호출하려면 백엔드가 공개 HTTPS여야 함.
```bash
tailscale funnel 8787        # → https://<node>.<tailnet>.ts.net
```
⚠️ **최초 1회: 테일넷 관리자가 Funnel 활성화 필요** — `tailscale funnel` 실행 시 출력되는
`https://login.tailscale.com/f/funnel?node=...` 링크를 (관리자 계정으로) 한 번 방문.
활성화 후 프런트(`assets/coupon.js`의 `API`)가 자동으로 서버 발급 사용. 미연결 시 로컬 발급(베타)로 폴백.

## 프런트 연동
`assets/coupon.js`:
- 로컬(localhost)→`http://127.0.0.1:8787`, 그 외→Funnel URL.
- `/health` 핑으로 "서버 연결됨/오프라인" 표시. 발급은 서버 우선, 실패 시 로컬 폴백.

## 도커 (이식용 — 서버 PC 오면 그대로) ★
스위치 온/오프 + 서버 PC 이식을 위해 컨테이너로 패키징. 미니PC든 서버 PC든 동일.
```bash
cd server
./up.sh            # 온 — docker compose up -d --build (health 자동확인)
./down.sh          # 오프 — compose down (데이터 ./data 보존)
IROS_DEVICE=<폰IP:포트> ./up.sh   # 서버 PC선 연결된 폰 IP 지정
```
- `Dockerfile`: python:3.12-slim + android-tools-adb + websocket-client. 그 외 표준 라이브러리.
- `docker-compose.yml`: `network_mode: host`(실기기 ADB·CDP forward 접근), `restart: unless-stopped`,
  `./data`에 쿠폰 DB·세션 산출물 영속 → **이식 시 `./data` 폴더만 옮기면 데이터 보존.**
- up.sh/down.sh는 docker compose 없으면 `docker run` 자동 폴백(이식성).
- 검증: 이미지 빌드·컨테이너 쿠폰발급·컨테이너 내 adb 1.0.41·라이브 전환(데이터 보존)·공개URL E2E 확인(2026-10-22).
- 공개 터널: compose의 `cloudflared` 서비스 주석 해제(임시 URL) 또는 서버 PC 고정도메인/Funnel.

## 상주(재부팅 생존)
도커(`restart: unless-stopped`)면 재부팅 자동 복구. 비도커는 systemd user 서비스.

## 다음 (실서비스화)
1. **Funnel 활성화**(관리자 1클릭) → 공개 라이브.
2. PG(토스/카카오페이 등) 결제 연동 → 유료권 `pending_payment`→`active`.
3. redeem→ADB/AutoJS6 세션 오케스트레이션 연결(열람 실행). ※ 열람 실행은 무VPN 로컬기기+점검종료 필요(FINDINGS).
