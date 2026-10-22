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
| GET | `/api/stats` | — | `{issued,redeemed}` (PII 없음) |

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

## 상주(재부팅 생존, 선택)
베타는 수동 실행으로 충분. 상시화는 systemd user 서비스 또는 기존 watchdog 패턴 사용.

## 다음 (실서비스화)
1. **Funnel 활성화**(관리자 1클릭) → 공개 라이브.
2. PG(토스/카카오페이 등) 결제 연동 → 유료권 `pending_payment`→`active`.
3. redeem→ADB/AutoJS6 세션 오케스트레이션 연결(열람 실행). ※ 열람 실행은 무VPN 로컬기기+점검종료 필요(FINDINGS).
