<#
.SYNOPSIS
  PC Eyes Watchdog — 헬스체크 + 세션 리마인더
  Windows CC 세션 시작 시 자동 실행. 모든 MCP 서버 상태 확인.
#>

$OK = "✅"; $NG = "❌"; $WA = "⚠️"
$DATE = Get-Date -Format "yyyy-MM-dd HH:mm KST"

Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗"
Write-Host "║       PC Eyes Watchdog — Windows GUI        ║"
Write-Host "╠══════════════════════════════════════════════╣"
Write-Host "║  $DATE"
Write-Host "╠══════════════════════════════════════════════╣"

# 1. desktop-touch-mcp (Rust UIA)
$dt = $NG
$nodePath = "C:\Program Files\nodejs"
$env:Path = "$nodePath;$env:Path"
try {
    $ver = node -e "try{console.log(require('@harusame64/desktop-touch-mcp/package.json').version)}catch(e){console.log('NOT_FOUND')}" 2>$null
    if ($ver -and $ver -ne 'NOT_FOUND') { $dt = $OK } else { $dt = $WA }
} catch { $dt = $NG }
Write-Host "║  $dt desktop-touch-mcp (Rust UIA v$ver)"
if ($dt -eq $NG) { Write-Host "║     → npm install -g @harusame64/desktop-touch-mcp" }

# 2. ScreenPilot (Python fallback)
$sp = $NG
$pyPath = "C:\Users\dtsli\AppData\Local\Programs\Python\Python312\python.exe"
$spPath = "C:\Users\dtsli\pc-eyes\ScreenPilot\main.py"
if ((Test-Path $pyPath) -and (Test-Path $spPath)) { $sp = $OK } else { $sp = $NG }
Write-Host "║  $sp ScreenPilot (Python fallback)"
if ($sp -eq $NG) { Write-Host "║     → pip install -r ScreenPilot/requirements.txt" }

# 3. Playwright (web bridge)
$pw = $NG
try {
    $pwVer = npx playwright --version 2>$null
    if ($pwVer) { $pw = $OK } else { $pw = $WA }
} catch { $pw = $NG }
Write-Host "║  $pw Playwright MCP (web bridge v$pwVer)"

# 4. PyAutoGUI + Pywinauto
$pyAuto = if (python -c "import pyautogui" 2>$null) { $OK } else { $NG }
$pyWin = if (python -c "import pywinauto" 2>$null) { $OK } else { $NG }
Write-Host "║  $pyAuto PyAutoGUI / $pyWin Pywinauto"

Write-Host "╠══════════════════════════════════════════════╣"
Write-Host "║  📋 PC Eyes Quick Reference                  ║"
Write-Host "║                                              ║"
Write-Host "║  W1 REAPER:  desktop-touch → discover+act    ║"
Write-Host "║  W2 Adobe:  desktop-touch → SoM OCR          ║"
Write-Host "║  W4 콘솔:    ScreenPilot → 스크린샷+OCR     ║"
Write-Host "║  웹:         Playwright MCP → headless       ║"
Write-Host "╚══════════════════════════════════════════════╝"
Write-Host ""

# ── MCP config 검증 ──
$settingsPath = "$env:USERPROFILE\.claude\settings.json"
if (Test-Path $settingsPath) {
    $cfg = Get-Content $settingsPath -Raw | ConvertFrom-Json
    $mcpNames = $cfg.mcpServers.PSObject.Properties.Name
    Write-Host "MCP 등록 현황:"
    @('desktop-touch','screen-pilot','playwright') | ForEach-Object {
        $status = if ($_ -in $mcpNames) { $OK } else { $NG }
        Write-Host "  $status $_"
    }
}
Write-Host ""
