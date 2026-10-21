# START HERE — 받은 에이전트용 지도

| 칸 | 파일 |
|---|---|
| 1 실패 기록 | journal/failures.md |
| 2 결정 이유 | AGENTS.md §6 (일부러 안 만든 것과 이유) |
| 3 절대 바꾸지 말 것 | AGENTS.md §2 (불변식 — 버그 아님) |
| 4 바꿔도 되는 것 | AGENTS.md §3, §8 |
| 5 검증 | AGENTS.md §13·§14, selfcheck.py, repro_test.py |

설치 없이 쓰려면: `./build_skill.sh` → `dist/legal-brain-skill.zip` 을 Claude 앱 스킬로 업로드(브라우저 불필요).

이 MCP: 한국 전자소송(소액 민사) 본인소송을 돕는 조회·계산·기록 도구 + **그걸 만들며 겪은 경험 전체**. 코드는 경험의 실행 가능한 요약본이다.

1. `AGENTS.md` — 불변식(§2) · 바꿀 것(§3) · 일부러 안 만든 것(§6) · 검증(§7)
2. `journal/01~03` — 시행착오 이야기 (사건 정보 가림)
3. `KNOWLEDGE.md` · `ASSESSMENT.md` — 절차·교훈·영상 분석 / 사건 평가 틀
4. `demo/sample-case/` — 사건 폴더 형식
5. 코드 → 수정 후 `python3 selfcheck.py`
