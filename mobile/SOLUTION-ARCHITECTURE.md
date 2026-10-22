# 솔루션 아키텍처 — "서버는 연산, 폰은 PII+실행"

> 등기(IROS) 열람/발급을 **PC 없이 모바일에서** 돌리는 완전 설계.
> 핵심 제약: **개인정보는 각 유저 폰에만. 서버는 PII를 절대 안 받는다.**
> 2026-10-22 · 커뮤니티/OSS/논문 리서치 종합.
> 💻 서버/기기/컴퓨트 사양 → [`REQUIREMENTS.md`](../REQUIREMENTS.md) (결론: 기본 설계엔 GPU 불필요, H200은 AI 두뇌 내재화 시에만).

---

## 0. 결론 — 네 설계는 검증된 패턴이다
"서버가 오케스트레이션, 폰이 실행, PII는 로컬에만" = 학술·OSS에 이미 확립된 **Edge-Cloud 프라이버시 분리** 패턴.
> 연구 요지: 로컬 에이전트가 화면을 읽고 **PII를 기기에서 익명 플레이스홀더로 치환** → 서버 LLM엔 **익명 구조만** 전송 → 서버가 '무엇을 누를지' 지시 → **로컬 프록시가 원래 값으로 복원해 폰에서 실행.** 네트워크에 **PII 원문 0.**

---

## 1. 아키텍처
```
┌──────────── 유저 폰 (PII 금고 + 실행) ────────────┐        ┌──── 서버 (연산, PII 無) ────┐
│  로컬 에이전트 (atx-agent / uiautomator2)          │        │  오케스트레이터 (LLM)         │
│  · IROS 세션·주소·등기결과·결제 = 전부 폰 안       │  ⇄     │  · "등기 열람" 의도 파싱       │
│  · PII → 플레이스홀더 치환 후 익명 구조만 업로드    │ Tailscale│ · 추상 명령 생성(주소=토큰)   │
│  · 서버 지시를 원래 값으로 복원 → 로컬 탭/입력 실행 │ /WSS    │  · 어느 화면 어느 버튼인지만  │
│  · 결제·인증 승인 = 사람(폰)                       │        │  · PII 원문 절대 수신 안 함   │
└────────────────────────────────────────────────┘        └──────────────────────────┘
```
- **폰이 손+금고**, **서버가 두뇌.** 민감정보는 경계(폰)를 안 넘는다.
- 서버가 하는 일: 요청 해석·플로우 결정·OCR/비전 보조(익명화된 것만). 무거운 LLM 연산.
- 폰이 하는 일: 실제 GUI 조작, PII 보관·복원, 결제 승인.

---

## 2. ADB 백그라운드 실행 (PC 없이 폰 자체에서)
| 방법 | 내용 | 비고 |
|---|---|---|
| **무선 ADB (Android 11+)** | 폰 Termux에서 `adb pair`→`adb connect`로 **자기 자신에 연결** | **PC 불필요.** 페어링포트(일시)+연결포트(고정) 2단계 |
| **atx-agent** (uiautomator2) | 기기에 상주하는 HTTP 서비스가 UI 구동 | 백그라운드 서비스로 상주 |
| **Shizuku** | 비루트 ADB급 권한을 앱에 부여 | ⚠️ **삼성 One UI가 백그라운드서 잘 죽임** → start-on-boot 포크 + watchdog + Tasker/Automate 재시작 |
| **Tailscale 상주** | `adb tcpip`를 Tailscale IP에 고정 → 세션 넘어 지속 | 서버-폰 터널 |
| **포그라운드 서비스 + wake lock** | OS 배터리킬 회피 | 상시 가동 |

### ⚠️ 정직한 한계 — "완전 백그라운드(화면 끄고)"는 GUI 자동화의 벽
- UI 자동화는 **화면이 렌더돼야** 탭이 먹는다. 화면 완전 off면 GUI 조작 불가(앱에 따라).
- 현실적 해법: **화면 켜두되 백라이트 조광(dim) + 포그라운드 서비스.** 또는 작업 순간만 화면 on.
- 등기 열람은 **수 초~십 수 초** 작업이라 이 제약이 가볍다(장시간 아님).

---

## 3. 오픈소스 빌드블록 (커뮤니티/레딧/깃허브)
| OSS | 역할 | 네 설계와 |
|---|---|---|
| **android-agent-automator** (dragonballls) | AI 에이전트가 실폰을 ADB로 구동 · 62 MCP툴 · 화면 스트리밍 · 다기기 잡큐 · 로컬/클라우드 LLM 교체 | ★ 서버-폰 분리 + MCP = 거의 동일 청사진 |
| **agent-device** (callstack) | 모바일 자동화 CLI + **MCP 서버** | ★ 네 MCP 스택에 바로 |
| **GADS** | 셀프호스트 디바이스팜 · 원격제어 + Appium | 다유저 폰 오케스트레이션 |
| **uiautomator2 / Auto.js** | 비루트 UI 자동화 엔진 | 폰 로컬 실행 |
| **Shizuku(+fork)** | 비루트 ADB 권한 | 백그라운드 권한 |

---

## 4. 서비스 제공 모델
1. **유저 온보딩:** 앱(또는 Termux 스크립트) 설치 → 폰에 로컬 에이전트 1회 세팅(무선ADB 페어링).
2. **서버 = 구독형 오케스트레이터** (SaaS). 유저별 잡큐.
3. **실행:** 유저가 "내 아파트 등기 떼줘" → 서버가 플로우 지시 → **유저 폰이 유저 IROS에서 유저 결제로 발급** → PDF는 폰에.
4. **과금:** 월 구독 또는 건당(서버 연산비). 등기 수수료·PII는 안 건드림.

---

## 5. 법적 · 프라이버시 결론
- **대행 아님:** 본인 폰·본인 세션·본인 결제 = 셀프. (등기 열람/발급은 공개등기라 더 안전)
- **개인정보보호:** PII가 서버로 안 감 = 유출면 최소. 개인정보보호법·마이데이터 흐름과 정합.
- **등기 신청(소유권이전 등)**만 법무사법 경계 → 열람/발급 중심으로 시작.

---

## 6. 1호 구현 범위 (최소 성공작)
- 대상: **IROS 부동산 등기 '열람'** (인증서 不要, 결제만).
- 폰: Galaxy + 무선ADB + uiautomator2.
- 서버: 주소 파싱 → 플로우 지시(익명). 결제 승인 = 사람.
- 산출: 열람 결과 캡처/PDF, 폰에 저장.

## 출처
- [Shizuku 백그라운드/삼성 킬 회피 (Tasker)](https://tasker.helprace.com/i1550-use-shizuku-as-background-alternative-to-adb-and-or-root)
- [무선 ADB + Termux + Tailscale 지속연결](https://github.com/bashycodes/marketplace/pull/4)
- [android-agent-automator (서버-폰·MCP·LLM교체)](https://github.com/dragonballls/android-agent-automator)
- [agent-device (MCP 모바일 자동화)](https://github.com/callstack/agent-device)
- [GADS 셀프호스트 디바이스팜](https://github.com/shamanec/GADS)
- [Mobile GUI Agent 익명화 프라이버시(arxiv)](https://arxiv.org/html/2602.10139v3)
- [Edge-first 프라이빗 AI 에이전트](https://petronellatech.com/blog/edge-first-ai-agents-offline-private-frontline-ready/)
