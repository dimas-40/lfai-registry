# iros/test — 실기기(Tab S9) ADB+CDP 테스트 하네스

> 실기기에서 m.iros 구조를 떠서 셀렉터 매핑(셀프힐링 기준점) 하기 위한 테스트.

## 절차
```bash
./connect.sh 100.86.15.50:5900     # ADB 연결 + CDP 포워드 + 포그라운드앱 확인
python3 recon.py pages             # ★읽기전용 — 열린 탭 목록(화면 안 바꿈)
python3 recon.py dump              # ★상태변경 — m.iros 새탭+구조+스샷 (유휴 크롬에서만!)
```
- `pages` = GET /json/list (urllib). 안전. 연결 확인용.
- `dump` = CDP /json/new + WS. **다른 세션이 크롬 쓰는 중이면 금지**(connect.sh 의 FOREGROUND·탭목록 먼저 확인).
- 셀 실행(youthful_borg, --network=host): `docker exec youthful_borg python3 /app/out/iros_recon/recon.py pages`

## 검증됨 (2026-10-22)
- Tab S9(SM-X716N) ADB(Tailscale 100.86.15.50:5900) 연결 ✅
- 크롬 CDP 서빙(Chrome 155) ✅ · `pages` 42탭 즉시 읽음 ✅
- playwright connect_over_cdp 는 안드로이드 크롬서 멈춤 → **CDP HTTP/WS 직결로 해결**

## 의존
- 호스트: android-tools(adb)
- dump: `pip install websocket-client`
