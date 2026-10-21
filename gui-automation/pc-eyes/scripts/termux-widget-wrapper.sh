#!/bin/bash
# ============================================================
# Termux Widget Wrapper — PC Eyes Watchdog + WSL 접속
# 설치: 폰 ~/.shortcuts/pc-eyes.sh 로 복사
# ============================================================

PC_EYES_WIN_IP="100.81.24.124"
SSH_PORT="22"
WSL_SSH_PORT="2222"

# ── 1. PC Eyes 헬스체크 (Windows SSH 경유) ──
check_pc_eyes() {
    local result
    result=$(ssh -p $SSH_PORT -o ConnectTimeout=5 -o StrictHostKeyChecking=no \
        dtsli@$PC_EYES_WIN_IP \
        "powershell.exe -Command \"try{node -e 'console.log(\\\"OK\\\")' 2>\$null}catch{console.log(\\\"NG\\\")}\"" \
        2>/dev/null)

    if echo "$result" | grep -q "OK"; then
        echo "✅ PC Eyes: ALL ACTIVE"
        return 0
    else
        echo "⚠️  PC Eyes: Windows 연결 실패"
        return 1
    fi
}

# ── 2. Termux 알림 전송 ──
notify_pc_eyes() {
    local status=$1
    termux-notification \
        --id pc-eyes-watchdog \
        --title "👁️ PC Eyes Watchdog" \
        --content "$status" \
        --priority high \
        --led-color 00FF00 \
        --action "termux-open"
}

# ── 3. PC Eyes 상태 표시 ──
echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║     PC Eyes — Termux Watchdog               ║"
echo "╠══════════════════════════════════════════════╣"
check_pc_eyes
echo "╠══════════════════════════════════════════════╣"
echo "║  W1 REAPER: desktop-touch MCP               ║"
echo "║  W2 Adobe:  desktop-touch SoM OCR           ║"
echo "║  W4 콘솔:   ScreenPilot + OCR               ║"
echo "║  Web:       Playwright MCP                  ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── 4. WSL tmux 세션 접속 ──
echo "→ WSL Claude 세션 접속 중..."
ssh -p $WSL_SSH_PORT -o ConnectTimeout=5 -o StrictHostKeyChecking=no \
    dtsli@$PC_EYES_WIN_IP \
    "tmux attach -t phone_claude 2>/dev/null || tmux new -s phone_claude"
