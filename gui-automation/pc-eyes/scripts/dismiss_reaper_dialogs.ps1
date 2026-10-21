# Dismiss REAPER startup dialogs
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using System.Text;
public class Win {
    public delegate bool EnumDelegate(IntPtr hWnd, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumDelegate lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
    [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr hWnd, EnumDelegate lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern IntPtr GetDlgItem(IntPtr hWnd, int nIDDlgItem);
    [DllImport("user32.dll")] public static extern short GetClassName(IntPtr hWnd, StringBuilder lpClassName, int nMaxCount);
}
'@ -Language CSharp

$reaperPid = (Get-Process reaper -EA SilentlyContinue | Select-Object -First 1).Id
Write-Host "REAPER PID: $reaperPid"

# Collect all REAPER windows
$reaperWindows = New-Object System.Collections.ArrayList
$cb = [Win+EnumDelegate]{
    param($hwnd, $lParam)
    $procId = [uint32]0
    [Win]::GetWindowThreadProcessId($hwnd, [ref]$procId) | Out-Null
    if ($procId -eq $script:reaperPid) {
        $sb = New-Object System.Text.StringBuilder 512
        [Win]::GetWindowText($hwnd, $sb, 512) | Out-Null
        $sb2 = New-Object System.Text.StringBuilder 128
        [Win]::GetClassName($hwnd, $sb2, 128) | Out-Null
        $script:reaperWindows.Add([PSCustomObject]@{
            HWND = $hwnd.ToString('x8')
            Title = $sb.ToString()
            Class = $sb2.ToString()
        }) | Out-Null
    }
    return $true
}
[Win]::EnumWindows($cb, [IntPtr]::Zero) | Out-Null

Write-Host "`n=== All REAPER windows ==="
$reaperWindows | Format-Table HWND, Class, Title -AutoSize

# Find and handle "Replace missing file" dialog
$missingDialog = $reaperWindows | Where-Object { $_.Title -like '*Replace missing file*' }
if ($missingDialog) {
    $hwnd = [IntPtr]::Parse($missingDialog.HWND, [System.Globalization.NumberStyles]::HexNumber)
    Write-Host "`n=== Found 'Replace missing file' dialog: HWND=$($missingDialog.HWND) ==="

    # Enumerate child windows to find buttons
    $children = New-Object System.Collections.ArrayList
    $childCb = [Win+EnumDelegate]{
        param($chwnd, $clParam)
        $sb = New-Object System.Text.StringBuilder 512
        [Win]::GetWindowText($chwnd, $sb, 512) | Out-Null
        $sb2 = New-Object System.Text.StringBuilder 128
        [Win]::GetClassName($chwnd, $sb2, 128) | Out-Null
        $script:children.Add([PSCustomObject]@{
            HWND = $chwnd.ToString('x8')
            Title = $sb.ToString()
            Class = $sb2.ToString()
        }) | Out-Null
        return $true
    }
    [Win]::EnumChildWindows($hwnd, $childCb, [IntPtr]::Zero) | Out-Null
    Write-Host "Children of 'Replace missing file':"
    $children | Format-Table HWND, Class, Title -AutoSize

    # Send Cancel (IDCANCEL = 2) via WM_COMMAND
    Write-Host "Sending WM_COMMAND IDCANCEL to dismiss dialog..."
    [Win]::SendMessage($hwnd, 0x0111, [IntPtr]::2, [IntPtr]::Zero) | Out-Null
    Start-Sleep 1
} else {
    Write-Host "No 'Replace missing file' dialog found"
}

# Find and handle "EVALUATION LICENSE" dialog
$evalDialog = $reaperWindows | Where-Object { $_.Title -like '*EVALUATION*' }
if ($evalDialog) {
    $hwnd2 = [IntPtr]::Parse($evalDialog.HWND, [System.Globalization.NumberStyles]::HexNumber)
    Write-Host "`n=== Found 'EVALUATION LICENSE' dialog: HWND=$($evalDialog.HWND) ==="

    $children2 = New-Object System.Collections.ArrayList
    $childCb2 = [Win+EnumDelegate]{
        param($chwnd, $clParam)
        $sb = New-Object System.Text.StringBuilder 512
        [Win]::GetWindowText($chwnd, $sb, 512) | Out-Null
        $sb2 = New-Object System.Text.StringBuilder 128
        [Win]::GetClassName($chwnd, $sb2, 128) | Out-Null
        $script:children2.Add([PSCustomObject]@{
            HWND = $chwnd.ToString('x8')
            Title = $sb.ToString()
            Class = $sb2.ToString()
        }) | Out-Null
        return $true
    }
    [Win]::EnumChildWindows($hwnd2, $childCb2, [IntPtr]::Zero) | Out-Null
    Write-Host "Children of 'EVALUATION LICENSE':"
    $children2 | Format-Table HWND, Class, Title -AutoSize

    # Try to click "Still evaluating" or close it
    # WM_CLOSE
    Write-Host "Sending WM_CLOSE to EVALUATION LICENSE dialog..."
    [Win]::SendMessage($hwnd2, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null
    Start-Sleep 1
}

# Check remaining windows after dismissing dialogs
$remainingWindows = New-Object System.Collections.ArrayList
$cb3 = [Win+EnumDelegate]{
    param($hwnd, $lParam)
    $procId = [uint32]0
    [Win]::GetWindowThreadProcessId($hwnd, [ref]$procId) | Out-Null
    if ($procId -eq $script:reaperPid) {
        $sb = New-Object System.Text.StringBuilder 512
        [Win]::GetWindowText($hwnd, $sb, 512) | Out-Null
        $script:remainingWindows.Add([PSCustomObject]@{
            HWND = $hwnd.ToString('x8')
            Title = $sb.ToString()
        }) | Out-Null
    }
    return $true
}
Start-Sleep 2
[Win]::EnumWindows($cb3, [IntPtr]::Zero) | Out-Null
Write-Host "`n=== Remaining REAPER windows ==="
$remainingWindows | Format-Table HWND, Title -AutoSize
