# PC Eyes v2 백서 — Windows 시각 GUI 자동화 스택 최종판

**버전**: v2.0  
**날짜**: 2026-06-22 KST  
**방법론**: W집합(v6) + 커뮤니티 메타(2026 상반기) + PC_EYES_REPORT 실측  
**저자**: PARKSY CTO × Claude Sonnet 4.6  
**레포**: `D:\PARKSY\dtslib-localpc\` · `C:\Users\dtsli\pc-eyes\`

---

## 0. 한 줄 정의

> **PC Eyes v2** = W1/W2/W4 Windows 성역을 위해, 에이전트가 데스크톱 GUI를 **UIA 정공 + Rust 속도 + 이미지 fallback**으로 보고 조작하는 MCP 눈 레이어.

웹(Playwright)은 WSL 본진에 맡기고, Windows 성역은 Windows 전용 도구로만 채운다.

---

## 1. 근거: 왜 이 조합인가

### 1.1 방법론: W집합에서 역산

| Windows 성역 | 작업 내용 | 필요한 눈 특성 |
|---|---|---|
| **W1** REAPER/ASIO | FX창 감지, Play+Record, VSTi 상태, 트랙 컨트롤 | UIA 정공 (REAPER 지원) + 빠른 응답 |
| **W2** 정밀 벡터 편집 | Adobe 패스 핸들, 버튼, 다이얼로그 | UIA + SoM 시각 fallback (Adobe UIA 불완전) |
| **W4** OS 기반 | diskpart, 복구 콘솔, BitLocker | 텍스트 스크린샷 + OCR (UIA 없음) |

### 1.2 커뮤니티 메타 2026: 세 가지 혁명

1. **Rust UIA 혁명**: `desktop-touch-mcp`가 PowerShell 기반 UIA 대비 **82배 속도 향상** 증명. 2026년 Windows GUI MCP의 표준이 Rust로 이동 중.
2. **MCP 표준화**: Anthropic MCP 프로토콜이 Windows GUI 자동화 시장을 통일. 더 이상 PyAutoGUI 스크립트를 따로 관리하지 않고, MCP 서버 하나로 모든 에이전트가 공유.
3. **Set-of-Marks 시각 fallback**: UIA가 잡을 수 없는 영역(게임, RDP, 커스텀 렌더링)을 OCR + 넘버링 박스로 극복. Adobe 같은 까다로운 앱도 눈을 달 수 있게 됨.

---

## 2. 최종 아키텍처

### 2.1 계층 구조

```
                        ┌──────────────────────────┐
                        │    Claude / 모든 에이전트   │
                        │  (MCP 프로토콜로만 소통)    │
                        └──────┬───────────────────┘
                               │
              ┌────────────────┼──────────────────┐
              │                │                   │
              ▼                ▼                   ▼
    ┌─────────────────┐ ┌──────────────────┐ ┌──────────┐
    │ desktop-touch   │ │   ScreenPilot    │ │ Playwright│
    │ -mcp (Rust)     │ │  (Python fallback)│ │ MCP      │
    │                 │ │                   │ │ (web)    │
    │ ▸ UIA 2ms       │ │ ▸ PyAutoGUI      │ │          │
    │ ▸ 29 tools      │ │ ▸ Pywinauto      │ │ ★기설치  │
    │ ▸ SoM OCR       │ │ ▸ 스크린샷       │ │ WSL영역  │
    │ ▸ token diff    │ │                   │ │          │
    └────────┬────────┘ └────────┬──────────┘ └──────────┘
             │                   │
             ▼                   ▼
      ┌──────────────┐  ┌──────────────┐
      │ W1 REAPER    │  │ W2 Adobe     │
      │ W4 콘솔      │  │ 커스텀 UI    │
      │ (UIA 정공)   │  │ (시각 fallback)│
      └──────────────┘  └──────────────┘
```

### 2.2 핵심 설계 결정

| 결정 | 이유 |
|------|------|
| **desktop-touch-mcp를 1순위로** | Rust UIA 2ms 응답 — REAPER 트랙 탐색이 PowerShell 대비 80배 빠름. 토큰 효율 60~80% (MPEG diff). W1에 최적 |
| **ScreenPilot은 fallback으로 유지** | 이미 설치 완료. desktop-touch-mcp가 못 잡는 영역(Adobe, 커스텀 렌더링)을 PyAutoGUI 기반으로 커버 |
| **Playwright는 WSL 영역으로 분류** | Windows 세션에 MCP 등록은 하지만, 실제로는 WSL 본진에서 웹 작업 처리. Windows에서는 브라우저가 필요한 극소수 케이스만 |
| **Cua는 Watch로 등록** | 16K+ stars, 백그라운드 synthetic cursor 혁신적. 하지만 QEMU VM overhead가 W1/W2에는 과함. 샌드박스 필요한 시점이 오면 설치 |

### 2.3 MCP 도구 비교 (Windows GUI 전용)

| MCP 서버 | 언어 | 속도 | 별 | W1 적합 | W2 적합 | 비고 |
|---|---|---|---|---|---|---|
| **desktop-touch-mcp** | Rust | ★★★★★ | ~1.5K⭐ | ✅✅ 최적 | ✅ SoM | **2026 핫. W1/W2 둘 다 커버** |
| Windows-MCP | Python | ★★★ | 4.7K⭐ | ✅ | ⚠️ | 범용. 설치 간편 |
| ScreenPilot | Python | ★★ | ~40⭐ | ✅ | ⚠️ | 이미 설치됨. fallback용 |
| UIA-X | Python | ★★ | Trending | ✅ | ⚠️ | 크로스플랫폼 |
| Cua | Rust+Py | ★★★ | 16K⭐ | ⚠️ overkill | ⚠️ | Watch. 샌드박스 필요 시 |

---

## 3. 커뮤니티 메타 2026 — 증거

### 3.1 Rust UIA 2ms 혁명 (desktop-touch-mcp)

```
- UIA 쿼리: PowerShell 164ms → desktop-touch 2ms (82×)
- UIA 트리 전체: 100ms (batch BFS)
- 스크린샷 diff: SSE2 SIMD 13~15× accelerate
- 토큰 효율: MPEG P-frame diff로 60~80% 절감
- Set-of-Marks: OCR → 클러스터링 → [1][2][3]... 번호 이미지 반환
- 29개 도구: discover → act / browser CDP / terminal / Excel VBA / macro
```

출처: npm `@harusame64/desktop-touch-mcp` v1.10.4 (2026-05-25)

### 3.2 @playwright/mcp 250K+ weekly installs (Microsoft)

Playwright MCP가 2026년 웹 자동화 MCP의 사실상 표준. `--vision auto` 모드로 accessibility tree + vision 하이브리드 지원. 보안 격리(Cloudflare serverless variant)까지 등장.

→ PC Eyes에서는 **WSL 영역**으로 편입. Windows 세션에 설치되어 있지만 실사용은 WSL 우회.

### 3.3 Cua 16K+ stars — "컴퓨터 사용" 인프라 표준

```
- YC X25 → 16,400+ GitHub stars
- Windows 백그라운드 synthetic cursor (2026-05-27)
- 3계층 입력: 픽셀(screenshot) + UIA/MSAA + action layer
- Multi-model: Claude, GPT-5, Gemini 2.5, Llama 4, Qwen
```

Cua는 W1/W2에 직접 쓰기엔 overhead가 크지만, 에이전트 샌드박스가 필요한 시점(외부 코드 실행, 격리 테스트)에는 최고의 선택.

---

## 4. W1 분석: REAPER/ASIO

### 4.1 현재 자동화 현황 (70% 흡수 완료)

| 작업 | 현재 | PC Eyes v2 |
|---|---|---|
| RPP 텍스트 생성 | ✅ WSL Python | 변화 없음 |
| recmode=5 설정 | ✅ RPP 템플릿 | 변화 없음 |
| Play+Record (action 1013) | ✅ WM_COMMAND | + desktop-touch-mcp: 버튼 위치 확인 가능 |
| FX 창 확인 | ❌ (Lua TrackFX_Show) | ✅ desktop-touch-mcp: "FX" 창 UIA 감지 |
| BBC SO 초기화 대기 | ❌ (타이머) | ✅ desktop-touch-mcp: SoM OCR로 "Loading..." 텍스트 감지 |
| WAV RMS 검증 | ✅ sox --stat | 변화 없음 |
| Telegram 배달 | ✅ curl API | 변화 없음 |

### 4.2 v2가 추가하는 것

- **FX 창 자동 감지**: desktop-touch-mcp의 `desktop_discover` → `wait_until`로 BBC SO FX 창이 열릴 때까지 폴링 (UIA 2ms)
- **"OFELINE" 감지**: PyAutoGUI 스크린샷 + SoM OCR로 "SOURCE MID FILE..." 텍스트 감지 → Python HASDATA 변환 자동 트리거
- **RecArm 상태 확인**: REAPER 트랙의 UIA TogglePattern으로 Arm 상태 읽기

---

## 5. W2 분석: 정밀 벡터 편집

### 5.1 한계 인정

Adobe Illustrator/Photoshop은 UIA 커버리지가 제한적이다. 베지어 핸들 같은 정밀 편집은 PyAutoGUI 좌표 클릭조차 의미가 없다(해상도/확대율/스크린 좌표 의존성 폭발).

### 5.2 PC Eyes v2의 역할 범위

| 작업 | 방법 | 담당 |
|---|---|---|
| AI 초안 → WSL 처리 → 파일 입고 | parksy-image 파이프라인 | ✅ WSL 완결 |
| **버튼 클릭**: "Export", "OK", "Save" | desktop-touch-mcp UIA or SoM | ✅ PC Eyes |
| **다이얼로그**: 포맷 선택, 해상도 설정 | desktop-touch-mcp UIA 콤보박스 | ✅ PC Eyes |
| **배치 처리**: 100개 파일 일괄 export | ExtendScript(JSX) 텍스트 트리거 | ✅ RPP 패턴 동일 |
| **베지어 핸들 조작** | ❌ 사람 손 | W2 성역 |

### 5.3 ExtendScript 자동화 (RPP 패턴 복제)

REAPER의 RPP 텍스트 생성과 동일한 패턴:

```javascript
#target illustrator
var doc = app.activeDocument;
var exportOpts = new ExportOptionsPNG24();
exportOpts.artBoardClipping = true;
exportOpts.horizontalScale = 200;
doc.exportFile(new File("output.png"), ExportType.PNG24, exportOpts);
```

PC Eyes가 이미지 내보내기 버튼 찾을 필요 없이, JSX 파일을 `app.doScript()`로 전송. 단, 이걸 하려면 Illustrator가 **스크립트 허용** 상태여야 함 (윈도우 → 환경설정 → 일반 → "스크립트에 파일 쓰기 및 네트워크 액세스 허용").

---

## 6. W4 분석: OS 기반

### 6.1 현실: BIOS/UEFI는 자동화 불가

diskpart, bcdedit, Windows 복구 콘솔은 텍스트 기반이어서 UIA가 없다. PC Eyes가 할 수 있는 것:

| 작업 | 방법 | 한계 |
|---|---|---|
| diskpart 스크립트 | PowerShell `.scr` 파일 실행 | 자동화 완료 |
| bcdedit 수정 | PowerShell 직접 | 자동화 완료 |
| BitLocker 상태 확인 | `manage-bde -status` | 자동화 완료 |
| **BIOS 설정 변경** | ❌ | 사람이 직접 (Dell F2 부팅) |

### 6.2 PC Eyes가 돕는 범위

W4는 **장애 시 트리거**다. 평소에는 필요 없지만, KB5083769 같은 사고가 터지면:

1. PC Eyes가 `desktop-touch-mcp`로 복구 콘솔 화면 캡처
2. 에러 텍스트를 OCR로 추출
3. 이슈 분석 → 수정 스크립트 생성
4. 박씨에게 Telegram 리포트 ("Step 1. diskpart 실행 → Step 2. ... ")

---

## 7. 설치 현황 + 추가 설치 계획

### 7.1 현재 (완료)

| 도구 | 위치 | 상태 |
|---|---|---|
| Playwright 1.61.0 + Chromium | global npm | ✅ |
| PyAutoGUI 0.9.54 | Python 3.12 | ✅ |
| Pywinauto 0.6.9 | Python 3.12 | ✅ |
| ScreenPilot | `C:\Users\dtsli\pc-eyes\ScreenPilot\` | ✅ |
| 프로젝트 폴더 | `C:\Users\dtsli\pc-eyes\` | ✅ |
| dtslib-localpc 연동 | `D:\PARKSY\dtslib-localpc\docs\pc-eyes.md` | ✅ |

### 7.2 추가 설치 (1순위)

```powershell
# desktop-touch-mcp (Rust UIA — 1순위)
npm install -g @harusame64/desktop-touch-mcp
```
설치 후 `C:\Users\dtsli\AppData\Roaming\Code\User\globalStorage\...` 또는 Claude Desktop settings.json에 MCP 등록.

### 7.3 Watch 리스트 (설치 보류)

| 도구 | 조건 |
|---|---|
| Cua | 에이전트 격리/샌드박스 필요 시 |
| Windows-MCP | desktop-touch-mcp가 W2 Adobe에서 실패할 경우 대체 |

---

## 8. MCP 등록 설정 (최종)

### 8.1 Claude Desktop / settings.json

```json
{
  "mcpServers": {
    "desktop-touch": {
      "command": "npx.cmd",
      "args": ["-y", "@harusame64/desktop-touch-mcp"]
    },
    "screen-pilot": {
      "command": "C:\\Users\\dtsli\\AppData\\Local\\Programs\\Python\\Python312\\python.exe",
      "args": [
        "C:\\Users\\dtsli\\pc-eyes\\ScreenPilot\\main.py"
      ]
    },
    "playwright": {
      "command": "npx.cmd",
      "args": ["-y", "@playwright/mcp"]
    }
  }
}
```

### 8.2 MCP 우선순위 (W1 기준)

1. `desktop-touch`: W1/W2 주력 (Rust UIA + SoM)
2. `screen-pilot`: W1/W2 fallback (PyAutoGUI)
3. `playwright`: WSL 브릿지용

---

## 9. 결론: v1→v2 변경 요약

| 항목 | v1 (PC_EYES_REPORT) | v2 (본 백서) |
|---|---|---|
| 주력 UIA 엔진 | ScreenPilot (Python, ~40ms) | **desktop-touch-mcp** (Rust, 2ms) |
| 웹 계층 | Playwright를 L1으로 | **WSL 영역으로 재분류** |
| W2 전략 | PyAutoGUI 이미지매칭 | **ExtendScript JSX + desktop-touch SoM fallback** |
| 토큰 전략 | 없음 | **MPEG P-frame diff로 60~80% 절감** |
| 커뮤니티 근거 | 없음 | **2026 메타: Rust UIA 혁명 + MCP 표준화** |
| Cua | 언급 없음 | **Watch 등록. 조건부 설치.** |
| dtslib-localpc 연동 | README 복사 | **docs/pc-eyes.md 정식 문서** |

---

## 10. 다음 액션 (우선순위)

| # | 액션 | 설명 |
|---|---|---|
| 1 | **desktop-touch-mcp 설치** | `npm install -g @harusame64/desktop-touch-mcp` |
| 2 | **MCP 등록** | settings.json에 3개 MCP 서버 등록 |
| 3 | **W1 테스트** | REAPER FX 창 감지 → Play+Record 자동화 |
| 4 | **W2 SoM 테스트** | Adobe Illustrator 버튼 탐색 + OCR |
| 5 | **ExtendScript 첫 스크립트** | "선택 영역 PNG 200% export" |

---

*끝. 이 문서는 dtslib-localpc/docs/pc-eyes.md에 저장됨.*  
*다음 판(v3) 갱신 조건: Cua 설치 결정 시 / W1 70%→90% 달성 시 / 새 MCP 메타 등장 시*
