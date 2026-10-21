# 075 — ecourt v1.0.0: 만점 명세 구현 + 실사건 파이프라인 1회 완주 (2026-10-03)

## 지시
박씨: "디렉션 다 줬으니 만점짜리 만들어, 구현해" + 앱 Claude v1.0 명세(P1~P5, 3계층, 위협 T1~T6, 평가 E1~E6, 감사로그, 어댑터, 릴리스) + 로펌 12기능 + v2(브라우저 분리·설치 없는 스킬).

## 한 일
- 구조: 법률 두뇌/브라우저(선택)/사건 저장소. CourtAdapter(KR-ECFS). 도구 32(브라우저 끄면 28)
- 모든 도구: annotation, 오류=데이터, 감사 로그(audit.jsonl), 상태 변경 dry_run 기본
- 사람 관문: elicitation(미지원 클라이언트는 confirm_read)
- 출처: 송달문서·판례 sha256·수신시각, 연표 출처 필수(출처 없는 행 거부 시험 통과)
- T3: checks.untrusted + 주입 문장 픽스처 테스트
- 로펌 12기능: firm.py (intake·chronology·strategy·exhibits·brief_draft·review_auto/packet·docket·WHY·closeout)
- selfcheck 35항목 ALL PASS, repro_test(맥락 없는 stdio 클라이언트·브라우저 끔·빈 데이터) REPRO PASS
- pre-push 훅: 비밀값 심은 임시 커밋 → 차단(exit 1) 확인
- 로컬 2차 백업: D:\PARKSY\backup\ecourt-private git bundle + post-commit 자동
- 이용약관 확인: 제15조(부정 접속·동의 없는 서비스 내용 가공·영리 이용·위변조 금지), 제14조②(인증장치 제3자 이용 금지). 자동화 명시 조항 없음 → B는 본인 사건·비영리, 공개 배포는 법원행정처 확인 후
- SKILL 원본 하나(로컬 스킬 → 레포 SKILL.md 심볼릭 링크), VERSION 1.0.0, CHANGELOG, 태그 ecourt-v1.0.0(로컬)

## 실사건 완주 (스프린트 1)
증거대장 19 → 연표 12행(출처) → 쟁점 6 → 초안 v1 → 기계 검토(확인필요 4) → **독립 검토 1회차 FAIL 8건**
→ 반영해 v2. 독립 검토가 잡은 가장 큰 오류: "피고가 접촉을 인정" 과장 — 앱 Claude와 Claude Code가 둘 다 밀었던 표현. 독립 검토 구조가 실제로 작동한 증거.

## 남은 것
독립 검토 2회차 결과 / 증거 확보(DB 출동내역서·구청·사고 전 사진·영상 접촉 시각) / OC 인증값 / 원격 백업·공개 결정 / 브라우저 열람 실시험 / 법원 알림 메일
