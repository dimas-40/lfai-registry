# 등기 전산 내비게이터 — 패키지 (Module 01 of LFAI AS)

> 하나의 패키지로: **설치 → 서식(유저 AI) → 자동입력(내비게이터) → 제출(유저 손가락).**
> 정체성: **셀프 등기 전산 내비게이터** (대행 아님). 서식 생성·결제·서명·제출의 주체는 유저.

## 구성
```
install.sh                      # 원클릭 설치(멱등) — 내비게이터 배치·브리지·안내
navigator/
  iros_register.js             # 등록 멀티스텝 자동입력 상태머신(채움→⏸승인대기→▶재개)
  guard.js                     # 결제·서명·제출 금지 라벨 차단
agent/
  master-system-prompt.md      # 유저 AI용 마스터 프롬프트(판단0·표준서식·법률자문 아님)
  run.sh                       # (선택) 파워유저 터미널 에이전트 실행
prompts/법인설립_서식_프롬프트팩.md  # 유저 AI가 서식 생성하는 범용 프롬프트
profile/법인설립_프로필.schema.json  # 내비게이터 입력용 로컬 데이터 계약(PII 로컬 전용)
index.html / app/              # PWA 앞단(쿠폰 발급·안내·시연)
```

## 두 레인 (온보딩)
- **A · 대중(설치 최소):** 웹 ChatGPT/Claude 에 프롬프트 붙여넣어 서식 → PWA에서 이용권 → "등기 도우미" 앱 1개 + 접근성 토글 1회 → 자동입력 → 제출(본인).
- **B · 파워유저:** LFAI 에이전트 설치기(lfai-as/learn/g)로 Claude Code(+DeepSeek, 유저 과금) 설치 → `mod add deunggi` → `deunggi draft` 로 서식 생성 → 내비게이터. (설치 장벽 낮음, 개발자/프로슈머)

## 흐름 (핸드오프)
```
유저 AI(서식 생성, 유저 과금)  ──profile.json──▶  내비게이터(AutoJS6, 온디바이스)
                                                    │ 정부 전산 멀티스텝 자동입력
                                                    ▼
                                           ⏸ 결제·전자서명·제출 = 유저 손가락
```

## 설치
```bash
pkg install -y curl && curl -O https://dimas-40.github.io/lfai-as/learn/g && bash g   # 베이스(한 번)
mod add deunggi                                                                 # 이 모듈
# (직접: curl -fsSL https://dimas-40.github.io/lfai-registry/install.sh | bash)
```
그다음 (1회 수동): ① 접근성 켜기 ② `deunggi draft`(또는 쓰던 AI)로 프로필 작성 ③ `deunggi run`.

## 내비게이터 모드 (브리지 cmd.json)
| op | 동작 |
|---|---|
| `health` | 엔진·현재앱 확인(기본) |
| `dump` | 현재 화면 노드 매핑 → `nodes.txt` (실기기 셀렉터 실측용) |
| `register` | 프로필로 멀티스텝 자동입력. 확정단계서 정지 |
| `resume` | 유저 승인 후 이어서 진행 |

## 법적 선 (요약 — 상세 strategy 문서)
- 서식 **생성 = 유저 AI**(우리 서버 아님). 우리는 **범용 양식 프롬프트 + 전산 내비게이터**만.
- 결제·전자서명·최종 제출 = **유저 손가락**(guard가 그 앞에서 정지).
- 로폼 대법 판례(2026): 빈칸채우기 자동입력·보조=합법 / 생성형AI 작성은 유저 쪽.
- "대행/법무사 대체" 표현 금지. 법률 자문 아님. 상용화 전 변호사 자문 1회.

## 상태 (정직)
- 플럼빙(설치·프롬프트·프로필·가드·상태머신 골격) = 작성 완료.
- ⚠️ 내비게이터 `STEPS[].sel`(실제 셀렉터)·실기기 풀런 = **무VPN 로컬기기에서 dump로 실측 필요**(미완).
