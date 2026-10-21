# CHANGELOG — ecourt

## 1.0.0 (2026-10-03) — devlog 074~075
- 구조: 법률 두뇌(A) / 브라우저(B, 선택: `ECOURT_BROWSER`) / 사건 저장소(C, 비공개). 어댑터 인터페이스 `CourtAdapter`(첫 구현 KR-ECFS)
- 도구 32(브라우저 끄면 28): 모두 annotation(readOnly/destructive/idempotent/openWorld), 오류=데이터, 감사 로그(append-only), 상태 변경은 dry_run 기본
- 사람 관문: 송달 열람은 MCP elicitation 또는 confirm_read
- 출처 체계: 송달문서 이미지·판례 본문 sha256·수신시각, 연표 행 출처 필수
- T3 문서 내 지시 주입 표시(`checks.untrusted`), 픽스처 테스트
- 로펌 12기능 파이프라인: intake·chronology·research(판례 채널·스크랩북)·strategy·brief_draft·review(기계+독립 에이전트)·docket·exhibits·opponent(베이즈·합의 구간)·rehearsal·explain(학습 모드)·closeout
- 골든 테스트 E1~E6 + 구조 검사(selfcheck), 맥락 없는 클라이언트 재현(repro_test), pre-push 차단 훅
- 설치 없는 스킬 패키지 `build_skill.sh` → legal-brain zip
- 실사건 검증: [사건번호] 준비서면 초안을 파이프라인으로 생성, 독립 검토 1회차 FAIL(8건) → 반영

## 0.3 (2026-10-03 오전) 판례 채널·상대 모델·맥락 배포 / 0.2 (10-03) 열람·계산·평가 / 0.1 (09-28) 조회 4도구·guard
