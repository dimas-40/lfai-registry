"""
PC Eyes — 전체 계층 통합 테스트
  Layer 1: PyAutoGUI (스크린샷 + 마우스/키보드)
  Layer 2: Pywinauto (윈도우 컨트롤 인식)
  Layer 3: Playwright (웹 DOM 기반)
  Layer 4: ScreenPilot (MCP 통합 GUI)

결과: pc-eyes\logs\test_report.txt
"""
import sys, os, platform, json
from datetime import datetime

REPORT = []
def log(msg):
    print(msg)
    REPORT.append(msg)

def section(title):
    sep = "=" * 60
    log(f"\n{sep}")
    log(f"  {title}")
    log(f"{sep}")

# ── 시스템 정보 ──
section("SYSTEM INFO")
log(f"Host:     {platform.node()}")
log(f"OS:       {platform.platform()}")
log(f"Python:   {sys.version}")

# ── Layer 1: PyAutoGUI ──
section("LAYER 1: PyAutoGUI (스크린샷 + 마우스)")
try:
    import pyautogui
    log(f"  Version:     {pyautogui.__version__}")
    w, h = pyautogui.size()
    log(f"  Screen:      {w} x {h}")

    # 스크린샷
    ss_path = os.path.join(os.path.dirname(__file__), '..', 'tests', 'ss_pyautogui.png')
    ss = pyautogui.screenshot(ss_path)
    log(f"  Screenshot:  {ss_path} ({ss.size})")

    # 마우스 위치
    mx, my = pyautogui.position()
    log(f"  Mouse pos:   ({mx}, {my})")

    log("  ✅ Layer 1: PyAutoGUI 동작 확인")
except Exception as e:
    log(f"  ❌ Layer 1 실패: {e}")

# ── Layer 2: Pywinauto ──
section("LAYER 2: Pywinauto (윈도우 컨트롤 인식)")
try:
    import pywinauto
    log(f"  Version:     {pywinauto.__version__}")

    from pywinauto import Desktop
    desktop = Desktop(backend="uia")
    windows = desktop.windows()
    log(f"  Visible windows: {len(windows)}")
    for i, w in enumerate(sorted(windows, key=lambda x: x.window_text())[:10]):
        text = w.window_text()[:60] if w.window_text() else "(no title)"
        log(f"    [{i}] {text}")
    if len(windows) > 10:
        log(f"    ... and {len(windows) - 10} more")

    log("  ✅ Layer 2: Pywinauto 동작 확인")
except Exception as e:
    log(f"  ❌ Layer 2 실패: {e}")

# ── Layer 3: Playwright ──
section("LAYER 3: Playwright (웹 DOM)")
try:
    # npm 전역 설치 확인
    import subprocess
    result = subprocess.run(
        ["node", "-e", "console.log(require('playwright/package.json').version)"],
        capture_output=True, text=True, shell=False,
        env={**os.environ, "PATH": r"C:\Program Files\nodejs;" + os.environ.get("PATH", "")}
    )
    pw_ver = result.stdout.strip()
    log(f"  Version:     {pw_ver}")

    # 브라우저 존재 확인
    import shutil
    browsers_path = os.path.expanduser(r"~\AppData\Local\ms-playwright")
    if os.path.isdir(browsers_path):
        dirs = os.listdir(browsers_path)
        log(f"  Browsers:    {len(dirs)} installed")
        for d in dirs:
            size = sum(os.path.getsize(os.path.join(browsers_path, d, f)) for f in os.listdir(os.path.join(browsers_path, d)) if os.path.isfile(os.path.join(browsers_path, d, f))) // (1024*1024)
            log(f"    - {d} ({size}MB)")

    # 간단한 Playwright 실행 테스트
    test_script = r"""
    const { chromium } = require('playwright');
    (async () => {
        const browser = await chromium.launch({ headless: true });
        const page = await browser.newPage();
        await page.goto('https://www.google.com', { waitUntil: 'domcontentloaded' });
        const title = await page.title();
        console.log('Browser test: OK, title=' + title);
        await browser.close();
    })();
    """
    result2 = subprocess.run(
        ["node", "-e", test_script],
        capture_output=True, text=True, timeout=30,
        env={**os.environ, "PATH": r"C:\Program Files\nodejs;" + os.environ.get("PATH", "")}
    )
    log(f"  Browser:     {result2.stdout.strip()}")
    if result2.stderr:
        log(f"  Stderr:      {result2.stderr.strip()[:200]}")

    log("  ✅ Layer 3: Playwright 동작 확인")
except Exception as e:
    log(f"  ❌ Layer 3 실패: {e}")

# ── Layer 4: ScreenPilot ──
section("LAYER 4: ScreenPilot (MCP GUI)")
try:
    sp_path = os.path.join(os.path.dirname(__file__), '..', 'ScreenPilot')
    sys.path.insert(0, sp_path)

    # 모듈 임포트 테스트
    from core.screen_capture import ScreenCapture
    from core.mouse import Mouse
    from core.keyboard import Keyboard
    from core.scroll import Scroll
    from core.element import Element
    from core.action_sequence import ActionSequence
    log(f"  Modules:     screen_capture / mouse / keyboard / scroll / element / action_sequence")

    # FastMCP 기반 config 확인
    import config
    log(f"  Server:      {config.SERVER_NAME}")
    log(f"  Format:      {config.DEFAULT_SCREENSHOT_FORMAT}")
    log(f"  Confidence:  {config.DEFAULT_CONFIDENCE}")
    log(f"  Screens dir: {config.SCREENS_DIR}")

    log("  ✅ Layer 4: ScreenPilot 동작 확인 (import OK)")
except Exception as e:
    log(f"  ❌ Layer 4 실패: {e}")

# ── 최종 요약 ──
section("SUMMARY")
success = sum(1 for l in REPORT if "✅" in l)
fail = sum(1 for l in REPORT if "❌" in l)
log(f"  Layers OK:  {success}/4")
log(f"  Layers FAIL: {fail}")
log(f"\n  Final verdict: {'✅ ALL SYSTEMS OPERATIONAL' if fail == 0 else '⚠️  NEEDS ATTENTION'}")

# 리포트 저장
report_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'test_report.txt')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(REPORT))
log(f"\nReport saved: {report_path}")
