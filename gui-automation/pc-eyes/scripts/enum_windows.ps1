param([int]$TargetPid = 0)

Add-Type @'
using System;
using System.Runtime.InteropServices;
using System.Text;
public class WndFinder {
    public delegate bool EnumWindowsDelegate(IntPtr hWnd, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsDelegate lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern IntPtr GetShellWindow();
}
'@

if ($TargetPid -eq 0) {
    $proc = Get-Process reaper -EA SilentlyContinue | Select-Object -First 1
    if (-not $proc) { Write-Host "REAPER not running"; exit 1 }
    $TargetPid = $proc.Id
}

$shellHWND = [WndFinder]::GetShellWindow()
Write-Host "Shell HWND: $($shellHWND.ToString('x8'))"
Write-Host "Target PID: $TargetPid"
Write-Host "---"

$list = New-Object System.Collections.ArrayList
$callback = [WndFinder+EnumWindowsDelegate]{
    param($hwnd, $lParam)
    $p = [uint32]0
    [WndFinder]::GetWindowThreadProcessId($hwnd, [ref]$p) | Out-Null
    if ($p -eq $TargetPid) {
        $sb = New-Object System.Text.StringBuilder 512
        [WndFinder]::GetWindowText($hwnd, $sb, 512) | Out-Null
        $vis = [WndFinder]::IsWindowVisible($hwnd)
        $list.Add([PSCustomObject]@{
            HWND = $hwnd.ToString('x8')
            Title = $sb.ToString()
            Visible = $vis
        }) | Out-Null
    }
    return $true
}

$enumPtr = [Runtime.InteropServices.Marshal]::GetFunctionPointerForDelegate($callback)
[WndFinder]::EnumWindows($enumPtr, [IntPtr]::Zero) | Out-Null

if ($list.Count -eq 0) {
    Write-Host "NO windows found for PID $TargetPid"
} else {
    $list | Format-Table HWND, Visible, Title -AutoSize
}
