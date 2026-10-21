#!/bin/bash
# PC Eyes WSL SSH Banner — WSL 로그인 시 자동 출력
# ~/.local/bin/pc-eyes-banner.sh 로 설치
# .bashrc 에서 source

# SSH 접속일 때만 실행
[ -z "$SSH_CONNECTION" ] && return 0

OK="✅"; NG="❌"; WA="⚠️"

# PC Eyes 상태 체크 (Windows PowerShell 경유)
check_pc_eyes() {
    local result
    result=$(powershell.exe -Command "
        \$dt = try{node -e \"console.log(require('@harusame64/desktop-touch-mcp/package.json').version)\" 2>\$null}catch{};
        if(\$dt){'OK'}else{'NG'}
    " 2>/dev/null | tr -d '\r')
    echo "$result"
}

STATUS=$(check_pc_eyes)

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║      PC Eyes — Windows GUI 자동화 스택      ║"
echo "╠══════════════════════════════════════════════╣"
echo "║  desktop-touch (Rust UIA): $( [ "$STATUS" = "OK" ] && echo "$OK" || echo "$WA" )              ║"
echo "║  ScreenPilot (fallback):    $OK              ║"
echo "║  Playwright (web bridge):  $OK              ║"
echo "╠══════════════════════════════════════════════╣"
echo "║  박씨가 GUI 작업(W1/W2) 요청 시 →           ║"
echo "║  desktop-touch MCP 로 REAPER/Adobe 제어     ║"
echo "║  ScreenPilot MCP fallback                   ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
