# 기술 표준 결정 — AutoJS6 온디바이스 + MCP

> 결론: 엔진은 **AutoJS6(온디바이스 접근성 JS) + AutoJs6-Plugin-MCP-Server(폰=MCP서버)**.
> ADB/Appium-MCP 무리는 "서버가 폰을 원격조종"이라 **참고(미러링)용**. 우리 니치 = **PII 로컬·PC 없음·일회성 토큰**.
> 2026-10-22 결정.

---

## 1. 지형 (ADB-MCP vs 온디바이스)
| 프로젝트 | 방식 | PC/ADB | PII | 라이선스 |
|---|---|---|---|---|
| mobile-mcp (mobile-next) | ADB+UIAutomator / WDA(iOS), 접근성우선 | **호스트 필요(off-device)** | 트리는 폰, 제어는 호스트 | Apache 2.0 |
| DroidRun / mobilerun | ADB + 비전 | 호스트 필요 | 비전=스샷 유출 | OSS+상용(€2.1M) |
| appium-mcp · adb-mcp · android-mcp-server | ADB/Appium | 호스트 필요 | 〃 | OSS |
| BrowserStack MCP | **디바이스팜(남의 기기)** | 클라우드 | 기기가 남의 것 | 상용 |
| **★ AutoJS6 + MCP 플러그인** | **온디바이스 접근성 JS, 폰=MCP서버** | **불필요(폰 자체)** | **폰에서 안 나감** | OSS |

## 2. 왜 AutoJS6인가 (우리 하드제약에 유일 정합)
- **온디바이스:** 폰 앱이 접근성으로 직접 실행 → **PII 로컬, PC/ADB 없음.**
- **이미 MCP:** `SuperMonster003/AutoJs6-Plugin-MCP-Server` — 폰이 MCP서버, **토큰 인증 Wi-Fi**, 37툴.
- **접근성(노드트리):** 비전/스샷 불필요 → **PII 유출 없이** 셀프힐링.
- **일회성:** .js 스크립트 = "다운로드→실행→만료"(Option B) 그 자체.
- **속도:** 접근성 기반 ~6ms급(일부 벤치 Appium 대비 100x).

## 3. 아키텍처 (합본)
```
[유저 폰]  AutoJS6 앱 + MCP 플러그인(토큰 Wi-Fi)
   └ IROS 열람 .js 스크립트를 접근성으로 로컬 실행 · PII 폰에만
        ▲ (서버가 밀어준 스크립트/업데이트)
[서버]  오케스트레이터
   └ IROS 플로우 JS 생성 · DOM 개편 시 중앙 self-heal → 새 .js 배포
   └ 익명 지시만. PII 수신 0.
```
- **엔진 = AutoJS6-MCP.** **두뇌/업데이트 = 서버.** **결제·서명 = 사람(폰).**

## 4. 미러링/리버스 엔지니어링 대상 (아이디어 흡수용)
| 레포 | 뽑을 것 |
|---|---|
| SuperMonster003/AutoJs6 | **본체 엔진** |
| SuperMonster003/AutoJs6-Plugin-MCP-Server | **MCP 서버(채택 베이스)** |
| mobile-next/mobile-mcp | 접근성 셀렉터 전략·툴 설계 |
| droidrun/mobilerun | 멀티스텝 플래닝·LLM 추상화 |
| Rahulec08/appium-mcp | 비주얼 요소 탐지·복구(폴백) |
| android-agent-automator | 다기기 잡큐·스트리밍 |

## 5. 다음
1. AutoJs6-Plugin-MCP-Server 설치·토큰 연동 실측(갤럭시)
2. IROS 열람 .js 1호 작성(접근성 셀렉터) — `iros/` 의 CDP판과 비교
3. 서버 self-heal 스크립트 배포 파이프라인

## 출처
- [AutoJs6 (SuperMonster003)](https://github.com/SuperMonster003/AutoJs6)
- [AutoJs6-Plugin-MCP-Server (37툴·토큰)](https://github.com/SuperMonster003/AutoJs6-Plugin-MCP-Server)
- [mobile-mcp (접근성우선 MCP)](https://github.com/mobile-next/mobile-mcp)
- [droidrun/mobilerun](https://github.com/droidrun/mobilerun)
- [appium-mcp](https://github.com/Rahulec08/appium-mcp)
