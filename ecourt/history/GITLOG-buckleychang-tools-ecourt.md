# 전자소송 MCP 커밋 이력 (buckleychang.com/tools/ecourt)

원본: ~/buckleychang.com tools/ecourt

```
5a45d6b | 2026-09-28 11:17:54 +0900 | tool(ecourt): 전자소송 조회 MCP — 전용 CDP Chrome·글자기반 클릭·금지버튼 가드·마감계산
40c6f18 | 2026-09-28 11:18:11 +0900 | fix(ecourt): 공개 사본 SKILL.md 에서 텔레그램 chat id 제거
df7285c | 2026-09-28 11:22:44 +0900 | docs: 레포 전체 파싱 — 두 층(어드바이저리 포털 / 나홀로 AI 교재)·연표·파일지도·가동상태·빈칸
3d54602 | 2026-10-03 08:56:18 +0900 | feat(ecourt): 송달문서 열람(open_service_doc, confirm_read 필수)·이자/과실상계 계산·사건노트 조회 도구, logged_in 오탐 수정, 절차 가이드(KNOWLEDGE.md)
1e66e34 | 2026-10-03 09:11:43 +0900 | feat(ecourt): 종합 사건평가 틀(ASSESSMENT.md, 6렌즈·학문 차용·역사), 기대값 도구(ecourt_expected_value), case_notes assessment/framework
9aa8b96 | 2026-10-03 09:25:38 +0900 | chore(ecourt): 로그인 아이디를 환경변수(ECOURT_USER_ID, ~/.config/ecourt/.env)로 분리, .env.example 추가
5410166 | 2026-10-03 09:32:51 +0900 | docs(ecourt): 영상 증거 분석 플러그 — Claude 프레임 한계, Gemini 1차 분석 분업, 업로드 주의
600478d | 2026-10-03 09:34:29 +0900 | docs(ecourt): Gemini 영상 분석 검증 규칙 — 블라인드 질문·시각 단위 주장·프레임 확인
804e68b | 2026-10-03 09:35:27 +0900 | docs(ecourt): 블라인드 영상 분석 기법(맥락 제거) 원조·대체 방법 기록
b35224c | 2026-10-03 09:39:37 +0900 | feat(ecourt): MCP 리소스(가이드·개발일지·사건문서)와 프롬프트(블라인드 영상 질문·변론 연습) 추가 — 코드뿐 아니라 이야기·지식 텍스트도 MCP 안에
8325fe8 | 2026-10-03 09:44:45 +0900 | feat(ecourt): 에이전트 대상 맥락 배포 — START_HERE·AGENTS(불변식·바꿀 것·의도적 미구현·검증), journal 01~03(가린 개발 이야기), demo 사건, selfcheck.py, ECOURT_DATA_DIR
a40b5d3 | 2026-10-03 10:04:25 +0900 | feat(ecourt): 실패기록 모음(failures.md)·START_HERE 5칸 지도·마스터맵 J01/R0~R2 연결·사건유형 교체표, 지인 실무자 자문 플러그(expert_consult), fault_table 출처 표시, selfcheck 민감정보 스캔
2988d87 | 2026-10-03 10:06:30 +0900 | docs(ecourt): 판례·법령·수사학 소스 지도(references/legal-sources.md) — 한국 Open API·MCP, 해외 판례 API, Perseus
f5609fb | 2026-10-03 10:10:37 +0900 | feat(ecourt): 판례 채널 — law_search_prec·law_get_prec·law_verify_case_no (국가법령정보 Open API 원문 + 로컬 캐시, LAW_OC env)
17c398c | 2026-10-03 10:11:37 +0900 | feat(ecourt): 판례 채널을 사건 스크랩북으로 — 쟁점 태그·관련성 메모·상태 칸(원문확보/인용검증/서면사용)·검색 기록(OC 미기록). 검색 본진은 korean-law-mcp 역할로 명시
d4e989f | 2026-10-03 10:11:48 +0900 | docs(ecourt): 판례 수집 기준 — 소액 유사사건이 아니라 쟁점별 상급심 법리, 과실비율 인정기준 별도
243690f | 2026-10-03 10:13:43 +0900 | docs(ecourt): 세계 전자소송 지형 — 범위(Range)·스코프(Scope) 문서
190b9d2 | 2026-10-03 10:28:06 +0900 | feat(ecourt): 상대 읽기 5층 모델 — 승소 분포 베이즈 갱신(case_update_belief·case_set_belief), 합의 구간(case_settlement_zone), 변론 질문 프롬프트(cross_exam_prep, 열린 질문·인신공격 차단)
520223a | 2026-10-03 10:40:05 +0900 | feat(ecourt): v1.0.0 — 법률 두뇌/브라우저 분리, 어댑터, 도구 annotation·오류=데이터·감사로그·dry_run, 사람 관문(elicitation), 출처 해시, 지시 주입 방어, 로펌 12기능 파이프라인, 골든 테스트 E1~E6, 재현 시험, pre-push 차단 훅, 설치 없는 스킬 패키지
69c5e96 | 2026-10-03 10:41:51 +0900 | fix(ecourt): 입증방법 기제출 조사(은)
c437491 | 2026-10-03 10:45:44 +0900 | feat(ecourt): 준비서면 초안 — 도입문에 답변서 일자, 본문 인용과 중복되는 인용 줄 생략, 입증방법 목록형(기제출 표시)
9373819 | 2026-10-03 15:34:13 +0900 | docs(ecourt): 만 19세 오픈 전략 백서 v2(역량 단계 학습 스케줄) + 참고문서 리소스 ecourt://reference/{name}
```
