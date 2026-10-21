# Find REAPER windows using Win32 API (works from any session context)
Add-Type -Name W -Namespace W32 -MemberDefinition @'
[DllImport("user32.dll")] public static extern bool EnumWindows(IntPtr lpEnumFunc, IntPtr lParam);
[DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder lpString, int nMaxCount);
[DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
[DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
[DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
[DllImport("user32.dll")] public static extern uint GetWindowModuleFileNameA(IntPtr hWnd, System.Text.StringBuilder lpszFileName, uint cchFileNameMax);
'@

# First take a screenshot using Windows built-in approach
Write-Host "=== Desktop State ==="
$fg = [W32.W]::GetForegroundWindow()
Write-Host "Foreground HWND: $($fg.ToString('x8'))"

# Get all reaper process IDs
$reaperProcs = @(Get-Process reaper -EA SilentlyContinue | Select-Object -ExpandProperty Id)
if ($reaperProcs.Count -eq 0) { Write-Host "REAPER not running"; exit 1 }
Write-Host "REAPER PIDs: $($reaperProcs -join ', ')"

$script:found = @()
$callback = @{
    Type = 'DelegateType'
    Value = [Func[IntPtr, IntPtr, bool]].MakeGenericType([IntPtr], [IntPtr])
}
$code = @'
$foundList = $script:found
$reaperPids = $script:reaperProcs
'@
# Manual EnumWindows
$def = @'
using System;
using System.Runtime.InteropServices;
using System.Text;
public class EnumWin {
    public delegate bool EnumDelegate(IntPtr hWnd, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumDelegate lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);
}
'@
Add-Type -TypeDefinition $def -Language CSharp

$found = New-Object System.Collections.ArrayList
$reaperSet = @{}; $reaperProcs | ForEach-Object { $reaperSet[$_] = $true }

$cb = [EnumWin+EnumDelegate]{
    param($hwnd, $lParam)
    $pid = [uint32]0
    [EnumWin]::GetWindowThreadProcessId($hwnd, [ref]$pid) | Out-Null
    if ($script:reaperSet.ContainsKey([int]$pid)) {
        $sb = New-Object System.Text.StringBuilder 512
        [EnumWin]::GetWindowText($hwnd, $sb, 512) | Out-Null
        $vis = [EnumWin]::IsWindowVisible($hwnd)
        $script:found.Add([PSCustomObject]@{HWND=$hwnd; PID=$pid; Title=$sb.ToString(); Visible=$vis}) | Out-Null
    }
    return $true
}

[EnumWin]::EnumWindows($cb, [IntPtr]::Zero) | Out-Null

if ($found.Count -eq 0) {
    Write-Host "NO REAPER windows found via EnumWindows"
} else {
    Write-Host "Found $($found.Count) REAPER window(s):"
    $found | Format-Table @{N='HWND';E={$_.HWND.ToString('x8')}}, PID, Visible, Title -AutoSize
}
