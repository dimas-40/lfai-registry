# List all processes with visible windows
$procs = Get-Process | Where-Object { $_.MainWindowHandle -ne 0 } | Sort-Object MainWindowTitle
Write-Host "=== Processes with MainWindowHandle != 0 ==="
$procs | Format-Table Id, ProcessName, MainWindowHandle, @{N='Title';E={$_.MainWindowTitle.Substring(0, [Math]::Min(60, $_.MainWindowTitle.Length))}} -AutoSize

# Check if reaper is running at all
$rp = Get-Process reaper -EA SilentlyContinue
if ($rp) {
    Write-Host "`n=== REAPER Process Details ==="
    $rp | Format-List Id, ProcessName, MainWindowHandle, MainWindowTitle, Responding, StartTime, TotalProcessorTime, WorkingSet64
}
