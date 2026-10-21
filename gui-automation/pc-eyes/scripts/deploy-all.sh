#!/bin/bash
# ============================================================
# PC Eyes 전체 배포 스크립트
# 3계층 강제 리마인더 시스템 설치
# ============================================================
# Windows PowerShell 관리자 권한 필요
# ============================================================

set -e

echo "╔══════════════════════════════════════════════╗"
echo "║   PC Eyes — 전 계층 강제 리마인더 배포      ║"
echo "╚══════════════════════════════════════════════╝"

# ── Layer 1: Windows 세션 Watchdog ──
echo ""
echo "[1/3] Windows Watchdog 설치"
WATCHDOG_PATH="C:\Users\dtsli\pc-eyes\scripts\watchdog.ps1"
if [ -f "$WATCHDOG_PATH" ]; then
    echo "  ✅ $WATCHDOG_PATH"
    echo "  ※ Windows CC 세션 시작 시 수동 실행:"
    echo "     powershell -File $WATCHDOG_PATH"
else
    echo "  ❌ Watchdog not found"
fi

# ── Layer 2: WSL SSH Banner (자동 실행) ──
echo ""
echo "[2/3] WSL SSH Banner 설치"
wsl -d Ubuntu -u dtsli bash -c '
    # 배너 스크립트 설치
    cat > ~/.local/bin/pc-eyes-banner.sh << '\''BANNER'\''
#!/bin/bash
[ -z "$SSH_CONNECTION" ] && return 0
OK="✅"; NG="❌"; WA="⚠️"
echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║      PC Eyes — Windows GUI Status           ║"
echo "╠══════════════════════════════════════════════╣"
STATUS=$(powershell.exe -Command "try{node -e 'console.log(String(require('"'\\''"'"@harusame64/desktop-touch-mcp/package.json"'"\\'"'").version))' 2>null}catch{console.log('NG')}" 2>/dev/null | tr -d '\''\r'\'')
if [ "$STATUS" != "NG" ]; then echo "  ✅ desktop-touch-mcp (v$STATUS)"; else echo "  ⚠️  desktop-touch-mcp: DOWN"; fi
echo "  ✅ ScreenPilot (Python fallback)"
echo "  ✅ Playwright MCP (web bridge)"
echo "╠══════════════════════════════════════════════╣"
echo "║  W1 REAPER → desktop-touch MCP              ║"
echo "║  W2 Adobe  → desktop-touch SoM OCR          ║"
echo "║  W4 콘솔   → ScreenPilot + OCR             ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
BANNER
    chmod +x ~/.local/bin/pc-eyes-banner.sh

    # .bashrc에 주입
    grep -q "pc-eyes-banner" ~/.bashrc 2>/dev/null || {
        echo "" >> ~/.bashrc
        echo "# PC Eyes banner (SSH login)" >> ~/.bashrc
        echo "[ -f ~/.local/bin/pc-eyes-banner.sh ] && source ~/.local/bin/pc-eyes-banner.sh" >> ~/.bashrc
    }
    echo "  ✅ WSL Banner 설치 완료"
'

# ── Layer 3: Termux 위젯 연동 ──
echo ""
echo "[3/3] Termux 위젯 스크립트"
echo "  📄 프로젝트 위치: C:\Users\dtsli\pc-eyes\scripts\termux-widget-wrapper.sh"
echo "  📱 폰 배포 방법:"
echo "     scp -P 8022 C:\Users\dtsli\pc-eyes\scripts\termux-widget-wrapper.sh \\"
echo "         dtsli@(폰IP):~/.shortcuts/pc-eyes.sh"
echo "     ssh -p 8022 dtsli@(폰IP) 'chmod +x ~/.shortcuts/pc-eyes.sh'"
echo ""

# ── 완료 ──
echo "╔══════════════════════════════════════════════╗"
echo "║   PC Eyes 강제 리마인더 시스템 배포 완료    ║"
echo "╠══════════════════════════════════════════════╣"
echo "║  Layer  Windows: watchdog.ps1 (수동 실행)   ║"
echo "║  Layer  WSL:     SSH 로그인 시 자동 배너    ║"
echo "║  Layer  Termux:  위젯 터치 시 상태 확인 후  ║"
echo "║                   WSL 접속                   ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
