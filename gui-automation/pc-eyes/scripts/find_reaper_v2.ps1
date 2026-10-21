# v2 - use $procId instead of $pid to avoid PS automatic variable conflict
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using System.Text;
public class EnumWin {
    public delegate bool EnumDelegate(IntPtr hWnd, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumDelegate lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr hWnd, out IntPtr lpRect);
}
'@ -Language CSharp

# Check foreground window
$fg = [EnumWin]::GetForegroundWindow()
Write-Host "Foreground HWND: $($fg.ToString('x8'))"

# Enumerate ALL windows to find desktop/program manager
$allWindows = New-Object System.Collections.ArrayList
$cb = [EnumWin+EnumDelegate]{
    param($hwnd, $lParam)
    $procId = [uint32]0
    [EnumWin]::GetWindowThreadProcessId($hwnd, [ref]$procId) | Out-Null
    $sb = New-Object System.Text.StringBuilder 256
    [EnumWin]::GetWindowText($hwnd, $sb, 256) | Out-Null
    $title = $sb.ToString()
    if ($title -ne '') {
        $script:allWindows.Add([PSCustomObject]@{
            HWND = $hwnd.ToString('x8')
            PID = [int]$procId
            Title = $title
        }) | Out-Null
    }
    return $true
}
[EnumWin]::EnumWindows($cb, [IntPtr]::Zero) | Out-Null
Write-Host "`n=== All visible windows ($($allWindows.Count)) ==="
$allWindows | Format-Table HWND, PID, @{N='Title(40)';E={$_.Title.Substring(0, [Math]::Min(40, $_.Title.Length))}} -AutoSize

# Specifically find REAPER
Write-Host "`n=== Searching for REAPER windows ==="
$reapers = $allWindows | Where-Object { $_.Title -match 'REAPER|reaper' }
if ($reapers) {
    $reapers | Format-Table -AutoSize
} else {
    Write-Host "No REAPER windows found"
}

# Check reaper process
$rp = Get-Process reaper -EA SilentlyContinue
if ($rp) {
    Write-Host "`n=== REAPER process details ==="
    $rp | Format-List Id, ProcessName, MainWindowHandle, MainWindowTitle, Responding, StartTime
}
