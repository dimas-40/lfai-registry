param(
    [string]$ProjectPath = "C:\Temp\mahler_bbcso_fixed.rpp"
)

$reaperExe = "C:\Program Files\REAPER (x64)\reaper.exe"

# Kill any existing REAPER
Get-Process reaper -EA SilentlyContinue | Stop-Process -Force -EA SilentlyContinue
Start-Sleep 3

# Start fresh
Write-Host "Starting REAPER with: $ProjectPath"
Start-Process -FilePath $reaperExe -ArgumentList "`"$ProjectPath`""

# Wait loop - up to 60 seconds
$maxWait = 60
$elapsed = 0
while ($elapsed -lt $maxWait) {
    Start-Sleep 2
    $elapsed += 2
    $proc = Get-Process reaper -EA SilentlyContinue
    if (-not $proc) { continue }

    # Check for main window
    $hwnd = $proc.MainWindowHandle
    $title = $proc.MainWindowTitle
    if ($hwnd -ne 0 -and $title -ne "") {
        Write-Host "REAPER ready: PID=$($proc.Id) HWND=$($hwnd.ToString('x8')) Title='$title' (${elapsed}s)"
        exit 0
    }

    # Check all windows
    $windows = @()
    try {
        $windows = Get-Process -Id $proc.Id -EA Stop | Select-Object -ExpandProperty MainWindowTitle
    } catch {}

    Write-Host "  ...waiting (${elapsed}s): hwnd=$($hwnd.ToString('x8')) title='$title'"
}

Write-Host "TIMEOUT: REAPER did not show main window after ${maxWait}s"
exit 1
