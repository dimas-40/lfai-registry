# IROS 온디바이스 자동화 (AutoJS6)

> `iros_yeollam.js` — IROS **앱**의 '부동산 열람'을 접근성으로 자동화. PC·ADB 불필요, 개인정보 폰에만.
> m.iros **웹**은 열람을 '앱 전용'으로 막으므로(실측, [`../FINDINGS.md`](../FINDINGS.md)) 이 앱 경로가 정답.
> 엔진 결정 근거: [`../../STANDARD.md`](../../STANDARD.md).

## 전제
- AutoJS6 6.7+ 설치 + **접근성 서비스 ON**.
- IROS 공식 앱 설치 + 로그인(간편인증 등은 사람이).
- 검증 기기(2026-10-22): Galaxy Tab S9(SM-X716N)에 AutoJS6 6.7.0 설치 확인. **IROS 앱 미설치 상태**라 full run 은 앱 설치 후.

## 모드 (cmd.json 의 `op`)
브리지: `/sdcard/Download/lfai/deunggi/` 의 `cmd.json`(입력) → `result.json`(결과, PII 미포함).

| op | 하는 일 |
|---|---|
| `health` | 엔진·현재 앱 확인(기본) |
| `dump` | 현재 화면 노드 매핑 → `nodes.txt`. **IROS 앱 설치 후 이걸로 `SEL` 채운다** |
| `yeollam` | 부동산 열람 플로우. `address`(★PII, 폰 로컬)로 검색 → 열람선택까지 → **결제 직전 정지** |

```jsonc
// 예: 열람 실행 (주소는 폰 로컬에서만)
{ "op": "yeollam", "address": "서울특별시 ..." }
```

## 안전장치 (guard)
- `FORBIDDEN` = 결제·납부·발급·서명·제출·인증·간편인증·카드·비밀번호·확정 … → **자동 클릭 절대 안 함**.
- `safeClick()` 가 모든 클릭 전 라벨 검사. 결제/인증 모달 감지 시 즉시 정지.
- 결제·발급 확정·서명 = **사람이 폰에서.** (등기 열람은 공개등기라 인증서 불요·결제만)

## 실행(참고)
AutoJS6 앱에서 스크립트 열어 실행하거나, 상주 워처(cmd.json 폴링) 패턴 사용.
> 접근성 ON·IROS 앱 설치·로그인은 기기 소유자 행위(개인정보·상태변경) — 코드가 대신 하지 않는다.

## 앱 설치 후 1회 셋업
1. IROS 앱 설치·로그인.
2. `{ "op":"dump" }` → `nodes.txt` 로 주소입력창/검색버튼/결과 라벨 확인.
3. `SEL` 의 text/desc/id 를 실측값으로 확정.
4. `{ "op":"yeollam", "address":"…" }` 로 결제 직전까지 구동 → 녹화해 랜딩 데모 증거로.
