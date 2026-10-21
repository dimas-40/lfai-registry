# IMPORT MANIFEST — 2026-10-21 이관 장부

총 94개 파일 · 개인·사건 식별자 41곳 마스킹

마스킹 규칙: 사건번호→`[사건번호]`, 상대방 보험사명→`[상대방 보험사]`, 원고 실명→`[원고]`, 관할 법원→`[관할 법원]`

**옮기지 않은 것 (원본 로컬에만 유지):** `~/ecourt-private/cases/`(실제 사건 서류), `identifiers.txt`, `audit.jsonl`, `law-search-log.jsonl`, 모든 `.env`(인증 값), `~/.config/ecourt/.env`, ScreenPilot `screens/`(실화면 캡처), `Screen Pilot.mp4`(10MB), 테스트 스크린샷, `ecourt/mcp/dist/`(build_skill.sh 빌드 산출물, 원본도 git 제외)

| 이 저장소 경로 | 원본 | 비고 |
|---|---|---|
| `ecourt/history/GITLOG-buckleychang-tools-ecourt.md` | `git log ~/buckleychang.com tools/ecourt` | 커밋 이력(마스킹) |
| `ecourt/history/GITLOG-ecourt-private.md` | `git log ~/ecourt-private ` | 커밋 이력(마스킹) |
| `ecourt/history/private-devlog/072-ecourt-ai-agent-workflow-2026-09-18.md` | `~/ecourt-private/072-ecourt-ai-agent-workflow-2026-09-18.md` | ecourt-private 개발일지(마스킹) |
| `ecourt/history/private-devlog/073-bojeong-submission-2026-09-28.md` | `~/ecourt-private/073-bojeong-submission-2026-09-28.md` | ecourt-private 개발일지(마스킹) |
| `ecourt/history/private-devlog/074-answer-received-assessment-mcp-2026-10-03.md` | `~/ecourt-private/074-answer-received-assessment-mcp-2026-10-03.md` | ecourt-private 개발일지(마스킹) |
| `ecourt/history/private-devlog/075-ecourt-v1-release-2026-10-03.md` | `~/ecourt-private/075-ecourt-v1-release-2026-10-03.md` | ecourt-private 개발일지(마스킹) |
| `ecourt/history/private-devlog/PENDING.md` | `~/ecourt-private/PENDING.md` | ecourt-private 개발일지(마스킹) |
| `ecourt/history/private-devlog/README.md` | `~/ecourt-private/README.md` | ecourt-private 개발일지(마스킹) |
| `ecourt/history/private-devlog/SKILL-ecourt-filing.md` | `~/ecourt-private/SKILL-ecourt-filing.md` | ecourt-private 개발일지(마스킹) |
| `ecourt/mcp/.env.example` | `~/buckleychang.com/tools/ecourt/.env.example` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/.gitignore` | `~/buckleychang.com/tools/ecourt/.gitignore` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/AGENTS.md` | `~/buckleychang.com/tools/ecourt/AGENTS.md` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/ASSESSMENT.md` | `~/buckleychang.com/tools/ecourt/ASSESSMENT.md` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/CHANGELOG.md` | `~/buckleychang.com/tools/ecourt/CHANGELOG.md` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/KNOWLEDGE.md` | `~/buckleychang.com/tools/ecourt/KNOWLEDGE.md` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/README.md` | `~/buckleychang.com/tools/ecourt/README.md` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/SKILL.md` | `~/buckleychang.com/tools/ecourt/SKILL.md` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/START_HERE.md` | `~/buckleychang.com/tools/ecourt/START_HERE.md` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/VERSION` | `~/buckleychang.com/tools/ecourt/VERSION` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/adapter.py` | `~/buckleychang.com/tools/ecourt/adapter.py` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/build_skill.sh` | `~/buckleychang.com/tools/ecourt/build_skill.sh` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/checks.py` | `~/buckleychang.com/tools/ecourt/checks.py` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/demo/fixtures/README.md` | `~/buckleychang.com/tools/ecourt/demo/fixtures/README.md` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/demo/fixtures/answer_sample.txt` | `~/buckleychang.com/tools/ecourt/demo/fixtures/answer_sample.txt` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/demo/sample-case/11_사건평가서_예시.md` | `~/buckleychang.com/tools/ecourt/demo/sample-case/11_사건평가서_예시.md` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/demo/sample-case/KNOWLEDGE_사건요약_예시.md` | `~/buckleychang.com/tools/ecourt/demo/sample-case/KNOWLEDGE_사건요약_예시.md` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/demo/sample-case/STATUS.md` | `~/buckleychang.com/tools/ecourt/demo/sample-case/STATUS.md` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/ecourt_mcp.py` | `~/buckleychang.com/tools/ecourt/ecourt_mcp.py` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/firm.py` | `~/buckleychang.com/tools/ecourt/firm.py` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/guard.py` | `~/buckleychang.com/tools/ecourt/guard.py` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/hooks/pre-push` | `~/buckleychang.com/tools/ecourt/hooks/pre-push` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/journal/01-소장접수-보정명령-사고.md` | `~/buckleychang.com/tools/ecourt/journal/01-소장접수-보정명령-사고.md` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/journal/02-보정서-제출.md` | `~/buckleychang.com/tools/ecourt/journal/02-보정서-제출.md` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/journal/03-답변서-평가-MCP확장.md` | `~/buckleychang.com/tools/ecourt/journal/03-답변서-평가-MCP확장.md` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/journal/failures.md` | `~/buckleychang.com/tools/ecourt/journal/failures.md` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/kr_calc.py` | `~/buckleychang.com/tools/ecourt/kr_calc.py` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/kr_deadline.py` | `~/buckleychang.com/tools/ecourt/kr_deadline.py` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/law_api.py` | `~/buckleychang.com/tools/ecourt/law_api.py` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/opponent.py` | `~/buckleychang.com/tools/ecourt/opponent.py` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/references/age19-open-strategy.md` | `~/buckleychang.com/tools/ecourt/references/age19-open-strategy.md` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/references/global-ecourt-range-scope.md` | `~/buckleychang.com/tools/ecourt/references/global-ecourt-range-scope.md` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/references/legal-sources.md` | `~/buckleychang.com/tools/ecourt/references/legal-sources.md` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/repro_test.py` | `~/buckleychang.com/tools/ecourt/repro_test.py` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/selfcheck.py` | `~/buckleychang.com/tools/ecourt/selfcheck.py` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/skill/legal-brain/SKILL.md` | `~/buckleychang.com/tools/ecourt/skill/legal-brain/SKILL.md` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/mcp/win_cdp.py` | `~/buckleychang.com/tools/ecourt/win_cdp.py` | buckleychang.com/tools/ecourt (MCP ecourt v1) |
| `ecourt/notes/memory-project_ecourt_gui_automation_prep.md` | `~/.claude/projects/-home-dtsli/memory/project_ecourt_gui_automation_prep.md` | Claude 메모리 사본(마스킹) |
| `ecourt/notes/memory-reference_global_ecourt_range_scope.md` | `~/.claude/projects/-home-dtsli/memory/reference_global_ecourt_range_scope.md` | Claude 메모리 사본(마스킹) |
| `ecourt/notes/인증서_PC모바일이전_준비_20260918.md` | `~/ecourt-private/인증서_PC모바일이전_준비_20260918.md` | 공동인증서 PC→모바일 이전 준비 |
| `ecourt/notes/전자소송포털_이용약관_20261003.txt` | `~/ecourt-private/전자소송포털_이용약관_20261003.txt` | 전자소송포털 이용약관(공개 문서) |
| `ecourt/pyauto/.env.example` | `~/ecourt-private/.env.example` | 환경변수 양식(값 없음) |
| `ecourt/pyauto/COORDINATES.md` | `~/ecourt-private/tools/COORDINATES.md` | ecourt-private GUI 좌표 자동화(마스킹) |
| `ecourt/pyauto/backup.sh` | `~/ecourt-private/tools/backup.sh` | ecourt-private GUI 좌표 자동화(마스킹) |
| `ecourt/pyauto/ecfs_pyauto.py` | `~/ecourt-private/tools/ecfs_pyauto.py` | ecourt-private GUI 좌표 자동화(마스킹) |
| `gui-automation/history/GITLOG-dtslib-localpc-pc-eyes.md` | `git log ~/dtslib-localpc pc-eyes` | 커밋 이력(마스킹) |
| `gui-automation/history/localpc-docs-pc-eyes.md` | `~/dtslib-localpc/docs/pc-eyes.md` | localpc 문서 |
| `gui-automation/history/papyrus-devlog-017-wsl-baseline-mcp-setup.md` | `~/dtslib-papyrus/docs/dev-logs/017-wsl-baseline-mcp-setup-2026-03-17.md` | MCP 기본 세팅 개발일지 |
| `gui-automation/mcp-servers.json` | `~/.claude.json mcpServers` | 명령·인자만, env 제외 |
| `gui-automation/pc-eyes/README.md` | `~/dtslib-localpc/pc-eyes/README.md` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/ScreenPilot/.gitignore` | `~/dtslib-localpc/pc-eyes/ScreenPilot/.gitignore` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/ScreenPilot/README.md` | `~/dtslib-localpc/pc-eyes/ScreenPilot/README.md` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/ScreenPilot/config.py` | `~/dtslib-localpc/pc-eyes/ScreenPilot/config.py` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/ScreenPilot/core/__init__.py` | `~/dtslib-localpc/pc-eyes/ScreenPilot/core/__init__.py` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/ScreenPilot/core/action_sequence.py` | `~/dtslib-localpc/pc-eyes/ScreenPilot/core/action_sequence.py` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/ScreenPilot/core/base_tool.py` | `~/dtslib-localpc/pc-eyes/ScreenPilot/core/base_tool.py` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/ScreenPilot/core/element.py` | `~/dtslib-localpc/pc-eyes/ScreenPilot/core/element.py` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/ScreenPilot/core/keyboard.py` | `~/dtslib-localpc/pc-eyes/ScreenPilot/core/keyboard.py` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/ScreenPilot/core/mouse.py` | `~/dtslib-localpc/pc-eyes/ScreenPilot/core/mouse.py` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/ScreenPilot/core/screen_capture.py` | `~/dtslib-localpc/pc-eyes/ScreenPilot/core/screen_capture.py` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/ScreenPilot/core/scroll.py` | `~/dtslib-localpc/pc-eyes/ScreenPilot/core/scroll.py` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/ScreenPilot/main.py` | `~/dtslib-localpc/pc-eyes/ScreenPilot/main.py` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/ScreenPilot/requirements.txt` | `~/dtslib-localpc/pc-eyes/ScreenPilot/requirements.txt` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/ScreenPilot/utils.py` | `~/dtslib-localpc/pc-eyes/ScreenPilot/utils.py` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/docs/PC_EYES_COMPLETE_REPORT.md` | `~/dtslib-localpc/pc-eyes/docs/PC_EYES_COMPLETE_REPORT.md` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/docs/PC_EYES_FINAL_v2.md` | `~/dtslib-localpc/pc-eyes/docs/PC_EYES_FINAL_v2.md` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/docs/PC_EYES_REPORT.md` | `~/dtslib-localpc/pc-eyes/docs/PC_EYES_REPORT.md` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/docs/PC_EYES_WHITEPAPER_v2.md` | `~/dtslib-localpc/pc-eyes/docs/PC_EYES_WHITEPAPER_v2.md` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/logs/test_report.txt` | `~/dtslib-localpc/pc-eyes/logs/test_report.txt` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/scripts/deploy-all.sh` | `~/dtslib-localpc/pc-eyes/scripts/deploy-all.sh` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/scripts/dismiss_reaper_dialogs.ps1` | `~/dtslib-localpc/pc-eyes/scripts/dismiss_reaper_dialogs.ps1` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/scripts/enum_windows.ps1` | `~/dtslib-localpc/pc-eyes/scripts/enum_windows.ps1` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/scripts/find_reaper.ps1` | `~/dtslib-localpc/pc-eyes/scripts/find_reaper.ps1` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/scripts/find_reaper_v2.ps1` | `~/dtslib-localpc/pc-eyes/scripts/find_reaper_v2.ps1` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/scripts/find_reaper_windows.ps1` | `~/dtslib-localpc/pc-eyes/scripts/find_reaper_windows.ps1` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/scripts/list_windows.ps1` | `~/dtslib-localpc/pc-eyes/scripts/list_windows.ps1` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/scripts/pc-eyes-wsl-banner.sh` | `~/dtslib-localpc/pc-eyes/scripts/pc-eyes-wsl-banner.sh` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/scripts/start_reaper.ps1` | `~/dtslib-localpc/pc-eyes/scripts/start_reaper.ps1` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/scripts/termux-widget-wrapper.sh` | `~/dtslib-localpc/pc-eyes/scripts/termux-widget-wrapper.sh` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/scripts/test_all_layers.py` | `~/dtslib-localpc/pc-eyes/scripts/test_all_layers.py` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/pc-eyes/scripts/watchdog.ps1` | `~/dtslib-localpc/pc-eyes/scripts/watchdog.ps1` | dtslib-localpc/pc-eyes (ScreenPilot MCP·Windows GUI 스크립트·보고서) |
| `gui-automation/phone-cdp/cdp.py` | `~/dtslib-papyrus/tools/meta/phone_cdp/cdp.py` | papyrus tools/meta/phone_cdp (안드로이드 크롬 CDP·ADB 조작) |
| `gui-automation/phone-cdp/ph.sh` | `~/dtslib-papyrus/tools/meta/phone_cdp/ph.sh` | papyrus tools/meta/phone_cdp (안드로이드 크롬 CDP·ADB 조작) |
| `gui-automation/phone-cdp/phc.py` | `~/dtslib-papyrus/tools/meta/phone_cdp/phc.py` | papyrus tools/meta/phone_cdp (안드로이드 크롬 CDP·ADB 조작) |
| `gui-automation/phone-cdp/phstep.py` | `~/dtslib-papyrus/tools/meta/phone_cdp/phstep.py` | papyrus tools/meta/phone_cdp (안드로이드 크롬 CDP·ADB 조작) |
