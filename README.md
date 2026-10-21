# lfai-registry

LFAI(엘에프에이아이) 등기 자동화 라인. 첫 자산으로 **전자소송 MCP**와 **GUI 자동화 도구**를 옮겨 왔다(2026-10-21).

## 범위 원칙 (먼저 읽을 것)

등기·소송 신청을 남 대신 하는 것은 법무사·변호사 업무다(법무사법). 이 저장소의 도구는 그 선을 넘지 않는다.

| 도구가 한다 | 사람이 한다 |
|---|---|
| 서식 기입 보조, 서류 준비, 기한 계산 | 최종 제출 |
| 진행 상태 조회, 기록·장부 | 공동·금융인증서 서명 |
| 화면 읽기, 좌표 이동 준비 | 클릭·저장·폼 제출(본인 동석) |

## 구성

```
ecourt/
├── mcp/            전자소송 MCP v1 (원본 buckleychang.com/tools/ecourt)
│                   ecourt_mcp.py · win_cdp.py(Windows 크롬 CDP) · guard.py · checks.py
│                   kr_deadline.py · kr_calc.py · law_api.py · firm.py · skill/ · demo/(가상 사건)
├── pyauto/         ecfs 화면 좌표 자동화 (ecfs_pyauto.py, COORDINATES.md)
├── history/        개발일지 072~075, 커밋 이력, journal(소장·보정·답변서 사고 기록)
└── notes/          인증서 PC→모바일 이전 준비, 전자소송포털 이용약관, 세계 전자소송 범위
gui-automation/
├── pc-eyes/        ScreenPilot MCP(Windows 화면 보기·클릭) + PowerShell 창 조작 스크립트 + 보고서·백서
├── phone-cdp/      안드로이드 크롬 CDP·ADB 조작 (Meta API 개통 때 사용)
├── history/        pc-eyes 커밋 이력, MCP 기본 세팅 개발일지
└── mcp-servers.json  ecourt · screen-pilot · desktop-touch 등록 명령 (env 제외)
```

## 개인정보

실제 사건 자료는 **옮기지 않았다**. 문서 속 사건번호·당사자·법원명은 마스킹했다. 상세는 [`MANIFEST.md`](MANIFEST.md).
원본 위치: `~/buckleychang.com/tools/ecourt`(코드 정본, 계속 사용 중), `~/ecourt-private`(사건 자료, 로컬 전용), `~/dtslib-localpc/pc-eyes`.

## 지금 이 저장소는

**사본**이다. MCP `ecourt`는 여전히 `buckleychang.com/tools/ecourt/ecourt_mcp.py`에서 돈다. 정본을 이쪽으로 옮길지는 결정 대기.
