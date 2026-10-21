Add-Type @'
using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;
public class WinAPI {
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
}
'@

$targetPid = $args[0]
if (-not $targetPid) {
    $proc = Get-Process reaper -EA SilentlyContinue | Select-Object -First 1
    if (-not $proc) { Write-Host "REAPER not running"; exit 1 }
    $targetPid = $proc.Id
}

Write-Host "Scanning windows for PID $targetPid..."
$found = @()
$cb = [WinAPI+EnumWindowsProc]{
    $p = [uint32]0
    [WinAPI]::GetWindowThreadProcessId($_, [ref]$p) | Out-Null
    if ($p -eq $targetPid) {
        $sb = New-Object System.Text.StringBuilder 256
        [WinAPI]::GetWindowText($_, $sb, 256) | Out-Null
        $found += [PSCustomObject]@{HWND=$_.ToString("x8"); Title=$sb.ToString()}
    }
    return $true
}
[WinAPI]::EnumWindows($cb, [IntPtr]::Zero) | Out-Null

if ($found.Count -eq 0) {
    Write-Host "No windows found for PID $targetPid"
} else {
    $found | Format-Table HWND, Title -AutoSize
}
