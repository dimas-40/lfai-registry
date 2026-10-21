# Dev Log 017 — WSL 베이스라인 확정 + Claude in Chrome 셋업

**날짜**: 2026-03-17  
**세션**: 집 PC WSL2 환경

---

## 오늘의 핵심 결정

### WSL2를 모든 PC 작업의 베이스라인으로 확정

**이유:**
- Claude Code가 Linux 네이티브 환경에서 가장 안정적
- 원격 접속(핸드폰 Termux → Tailscale SSH → WSL) 완벽 지원
- MCP 서버들 Linux 환경에서 안정적 실행
- Windows 설정 건드릴 필요 없음
- WSLg로 GUI 앱(Chromium)도 화면에 띄울 수 있음

---

## 오늘 삽질 요약 (반면교사)

### 네이버 로그인 자동화 10회 이상 실패

**원인:**
1. Playwright **스크립트** 작성 방식으로 접근 → 잘못된 방향
2. eccpw(암호화 PW) 미생성 → Naver JS 암호화 트리거 안됨
3. 반복 시도로 IP/계정 봇 차단 누적

**교훈:**
- GUI 강요 플랫폼은 **Claude in Chrome** 방식으로만
- 스크립트 파일 작성 방식 금지
- eccpw 암호화는 Naver JS가 처리 → 강제 bypass 불가

---

## 확정된 아키텍처

```
Claude Code (WSL2)
    ↓
    ├── Claude in Chrome → Windows Chrome → 플랫폼 GUI 자동화
    ├── Bash 도구 → 로컬 파일/명령 제어
    ├── GitHub MCP → 코드 관리
    └── 기타 MCP → Vercel, Notion 등
```

---

## GUI 플랫폼 자동화 원칙 (확정)

| 원칙 | 내용 |
|------|------|
| 엔진 | Claude in Chrome (Windows Chrome 직접) |
| 방식 | Claude 화면 직접 보면서 판단 (스크립트 작성 금지) |
| 모드 | headless=False (봇 감지 방지) |
| 대상 | 네이버, 티스토리, YouTube, 인스타, GCP 등 |

---

## 현재 MCP 상태

| MCP | 상태 |
|-----|------|
| Playwright (브라우저) | ✅ Connected |
| Vercel | ✅ Connected |
| AWS Marketplace | ✅ Connected |
| Mermaid | ✅ Connected |
| GitHub | 🔑 인증 필요 |
| Gmail / GCal | 🔑 인증 필요 |
| Figma, Notion 등 | 🔑 인증 필요 |

---

## 남은 작업

- [ ] 네이버 로그인 (parksy_kr, dtslib, eae_kr) → Claude in Chrome으로 재시도
- [ ] 티스토리 로그인
- [ ] YouTube OAuth
- [ ] GitHub MCP 인증
- [ ] npm run auto 실행

---

## 환경 스펙

- OS: Ubuntu 24.04.3 LTS (WSL2)
- Kernel: 6.6.87.2-microsoft-standard-WSL2
- Claude Code: 2.1.76
- Node.js: 20.20.1
- Playwright MCP: `env DISPLAY=:0 /usr/bin/playwright-mcp --browser chromium`
- WSLg: wayland-0 / DISPLAY :0
