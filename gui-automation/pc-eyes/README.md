# 👁️ PC Eyes — Windows 시각 GUI 자동화 스택

Claude Code가 Windows 환경에서 **웹 브라우저 + 데스크톱 GUI**를 보고 제어할 수 있게 하는 도구 모음.

## 디렉토리 구조

```
C:\Users\dtsli\pc-eyes\
├── README.md          ← 이 파일
├── docs/
│   └── PC_EYES_REPORT.md  ← 설치 리포트
├── scripts/
│   └── test_all_layers.py ← 통합 테스트
├── tests/
│   ├── ss_playwright.png  ← Playwright 스크린샷 테스트
│   └── ss_pyautogui.png   ← PyAutoGUI 스크린샷 (대화형 세션 필요)
├── logs/
│   └── test_report.txt    ← 테스트 로그
└── ScreenPilot/           ← MCP GUI 서버 (git clone)
    ├── main.py
    ├── core/
    │   ├── screen_capture.py
    │   ├── mouse.py
    │   ├── keyboard.py
    │   ├── scroll.py
    │   ├── element.py
    │   └── action_sequence.py
    └── requirements.txt
```

## 연동

- **dtslib-localpc 레포**: `D:\PARKSY\dtslib-localpc\`
- **참조 문서**: `D:\PARKSY\dtslib-localpc\docs\pc-eyes.md`
