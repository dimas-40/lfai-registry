# iros — 인터넷등기소 모바일 열람 자동화 MCP

> 아키텍처: `../MOBILE-AUTOMATION.md` · `../SOLUTION-ARCHITECTURE.md`
> **서버=연산(익명 길찾기), 폰=PII+실행(크롬 CDP).** 결제·발급·서명은 코드차단 → 사람(폰)만.

## 원칙
- 대상: `m.iros.go.kr` 부동산 등기 **열람**(공개등기 → 인증서 불요·결제만).
- **일회성 무선ADB**(페어링 코드=1회용 토큰)로 폰 연결 → 크롬 CDP 제어 → 세션 끝 폐기.
- **PII(주소·등기내용)는 폰을 안 떠난다.** 감사로그에도 PII 미저장.
- 셀렉터는 `iros_dump`로 매핑(사이트 개편 시 재매핑 = 셀프힐링 지점).

## 도구
| 도구 | 역할 | 등급 |
|---|---|---|
| `iros_connect` | 일회성 무선ADB 페어+연결 + CDP 포워드 | R1 |
| `iros_status` | 연결·URL 확인 | R0 |
| `iros_open` | 모바일 등기소 진입(길찾기, PII 없음) | R1 |
| `iros_dump` | 화면 구조만 덤프(셀렉터 재매핑·PII 미포함) | R0 |
| `iros_search_realty` | 부동산 열람 검색(결제 직전 정지) | R2 |
| `iros_disconnect` | 세션·토큰 폐기 | R1 |

## guard.py — 코드로 막는 것
결제 · 납부 · 발급확정 · 전자서명 · 제출 · 삭제 · 인증서 → **자동 클릭 불가. 사람만.**

## 실행
```bash
pip install -r requirements.txt
python3 -m playwright install chromium   # (연산측 아님, CDP는 폰 크롬에 붙음)
# 폰: 무선 디버깅 ON → 페어링 코드 확인
# claude mcp add iros -- python3 iros_mcp.py
```

## 다음(실기기 1회)
`iros_dump` → 검색창/열람 버튼 셀렉터 확인 → `iros_search_realty` TODO 채우기 → 열람 자동화 완성.
