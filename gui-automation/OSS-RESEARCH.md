# 오픈소스 커뮤니티 리서치 — 자동화 빌드 블록

> 목표: "사람이 시키면 에이전트가 GUI 작업을 대신 수행"(전자소송·폼 제출·앱 조작)하는 솔루션을
> **오픈소스로 조립**하기 위한 조사. 2026-10-21 자율 리서치.
> ★ = 박씨 기존 자산과 바로 연결되는 것.

---

## 1. 에이전트형 웹 자동화 (대행 엔진의 핵심)

### ★ Browser Use (MIT) — 1순위 범용 엔진
- OSS 중 최고 성능: **WebVoyager 89.1%**. DOM + 접근성 트리 + **CDP 직접 제어**.
- 커뮤니티 最大·반복 最速, 어떤 모델이든 물림, **MIT 라이선스(상업 자유)**.
- ★ **박씨 기존 CDP 방식(chrome_cdp/device-cdp)과 동일 계보** → 바로 흡수 가능.
- github.com/browser-use/browser-use

### ★ Skyvern (AGPL-3.0) — 폼 작성 특화 = 전자소송에 최적
- **WebVoyager 85.85%, 폼 작성 1위.** 비전 + DOM 동시 분석.
- 강점: **"여러 비슷한 사이트에서 다단계 신청서 작성·송장 다운로드·멀티스텝 양식 완성"** — 이게 바로 전자소송/민원 폼 반복 작성의 정체.
- ⚠️ **AGPL-3.0 = 카피레프트.** SaaS로 팔면 소스공개 의무 소지 → 상업화 시 라이선스 검토 필수(사내 사용은 무관).
- github.com/Skyvern-AI/skyvern

### 기타 (벤치 상위, 참고)
- **Stagehand**(브라우저 액션 프레임워크) · **UI-TARS**(비전 GUI) · **Agent S3** · **OpenAdapt**(사람 녹화→재현) · **UFO³**(윈도우).

---

## 2. 모바일 앱 자동화 (박씨 ADB 방식의 정식판)

### ★ uiautomator2 (openatx) — 네 raw ADB의 업그레이드
- Android UI Automator의 **Python 래퍼.** 기기에 HTTP 서비스 + 파이썬 클라이언트.
- **ADB 직결 · 비루트 · 시스템 앱까지 조작 · Appium 서버 불필요.** `pip install uiautomator2`.
- ★ 박씨 parksy-gallery MCP의 "`uiautomator dump` → XML 중심좌표" 수작업을 **라이브러리로 대체** → 코드 10배 단순·안정. **지금 당장 이식 권장.**
- github.com/openatx/uiautomator2

### Appium (+ appium-uiautomator2-driver)
- 표준이지만 서버 기반이라 무겁다. 여러 플랫폼 테스트용. 1인 자동화엔 uiautomator2가 가볍고 빠름.

---

## 3. 전자소송 — 현실 (★중요)

### 정부 시스템 = 폐쇄, 오픈소스 없음
- **나홀로소송** `pro-se.scourt.go.kr` (2010~): 흔한 민사(대여금·매매·보증금·임금)의 **소장을 직접 작성** 지원.
- **전자소송** `ecfs.scourt.go.kr` (2011~): 법원 안 가고 온라인 제출·진행 확인.
- 한국 전자소송 전용 **오픈소스 legaltech는 사실상 없음**(정부 폐쇄계, 보안프로그램·공인인증).

### 합법 모델 = "AI 초안 + 면허자 첨삭" (대행 아님)
- 상용 사례 **"어니언"**: **나홀로소송 AI 소장 → 변호사가 첨삭.** ← 이게 안전한 구조.
- ⚠️ **법원은 AI로 허위 판례·법령 인용 시 소송비용을 당사자에 부담**시킬 수 있음(2026).
- ⚠️ **타인 소장을 대신 작성·제출(대행) + 보수 = 변호사법/법무사법 위반 리스크.**
- → **권장 구조:** ① 본인이 직접 하도록 돕는 **셀프 자동화 툴/교재**(대행 X, 합법) ② 또는 **법무사·변호사 제휴**(면허자가 주체, 자동화 엔진만 공급).

---

## 4. RPA 프레임워크 (비개발자용 보조)
- **Robot Framework + rpaframework**: 키워드 기반, 파이썬 연동, 활발.
- **TagUI**: 평문 스크립트(비개발자 친화)지만 **AI Singapore 유지보수 중단**(커뮤니티 의존) → 신규 채택 주의.

---

## 5. 권장 스택 (박씨 목표 기준)
| 작업 유형 | 추천 OSS | 박씨 자산 연결 |
|---|---|---|
| 웹 폼·신청서(전자소송·민원) | **Skyvern**(폼) / **Browser Use**(범용·MIT) | CDP 스크립트 → 흡수 |
| 모바일 앱 조작 | **uiautomator2** | parksy-gallery ADB → 이식 |
| 오케스트레이션 | **박씨 MCP 레이어로 래핑** | 기존 FastMCP 패턴 |
| 전자소송 | 셀프툴 + **면허자 제휴**(어니언식) | — (대행 금지) |

**한 줄 설계:** 엔진은 Browser Use(MIT, 범용)로 깔고, 폼 반복은 Skyvern, 모바일은 uiautomator2, 전부 박씨 MCP로 묶는다. 전자소송은 "대행"이 아니라 "본인 셀프 + 변호사 첨삭"으로 가야 법적으로 산다.

---

## 출처
- [11 Best AI Browser Agents 2026 (Firecrawl)](https://www.firecrawl.dev/blog/best-browser-agents)
- [Computer-Use AI Agents 2026 (Turing Post)](https://www.turingpost.com/p/computer-use-ai-agents)
- [uiautomator2 (openatx)](https://github.com/openatx/uiautomator2)
- [appium-uiautomator2-driver](https://github.com/appium/appium-uiautomator2-driver)
- [uiautomator2 vs Appium](https://adbhandbook.com/blog/uiautomator2-vs-appium-android-automation)
- [대법원 나홀로소송](https://pro-se.scourt.go.kr/wsh/wsh000/WSHMain.jsp)
- [나홀로소송 AI 소장 '어니언' (파이낸셜포스트)](https://www.financialpost.co.kr/news/articleView.html?idxno=281129)
- [Top 7 Open Source RPA Tools (AIMultiple)](https://aimultiple.com/open-source-rpa)
- [RPA Framework docs](https://docs.robotframework.org/docs/different_libraries/rpa)
