# 모듈 계약 (LFAI AS 에이전틱 모듈 표준)

> 모든 스토어 모듈은 이 레이아웃을 따른다 → **LFAI 에이전트 설치기(베이스, lfai-as/learn/g)와 `mod add` 가 어떤 모듈이든 똑같이 설치**.
> 등기 = 1호 레퍼런스.

## 베이스 vs 모듈
- **베이스 = LFAI 에이전트 설치기** (한 번 설치): `pkg install -y curl && curl -O https://dimas-40.github.io/lfai-as/learn/g && bash g` → 에이전트(Claude Code · Aider, DeepSeek 키) + 위젯 + `mod` 명령.
- **모듈 = lfai-as 스토어 각 항목**(등기·세무·민원…): 베이스 위에 플러그인.

## 모듈 필수 구성 (레포 루트)
```
module.json          # 매니페스트(id·needs·provides·legal)
install.sh           # 멱등 설치(내비게이터 배치·브리지·안내)
navigator/           # AutoJS6 온디바이스 자동화(+guard)
prompts/             # 유저 AI용 범용 프롬프트(판단0·법률자문 아님)
profile/             # 로컬 데이터 스키마(PII 로컬 전용)
agent/               # (선택) 마스터 시스템 프롬프트
```

## 공리(모든 모듈 공통)
1. **서식·판단 = 유저 AI**(BYO). 우리 서버 생성 금지(로폼 판례).
2. **PII = 유저 폰 로컬.** 서버 수신 0.
3. **결제·서명·제출 = 본인 손가락.** guard가 그 앞에서 정지.
4. **포지셔닝 = 셀프 전산 보조 도구**(대행/전문직 대체 아님).

## 설치 흐름
```
pkg install -y curl && curl -O https://dimas-40.github.io/lfai-as/learn/g && bash g   # 베이스(에이전트)
mod add deunggi        # 모듈(등기) = lfai-as/mod/index.txt → lfai-registry/install.sh 실행
# 새 모듈은 lfai-as/mod/index.txt 에 한 줄(모듈ID 설치주소 이름) 추가
→ 접근성 1회 + 유저 AI로 서식 + 이용권 → 실행
```
