# PowerShell script to register Windows Task Scheduler for 24/7 Autopilot
param (
    [string]$Action = "register"
)

$TaskName = "AI_Instagram_Reels_Autopilot"
$ProjectDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Definition)
$BatchScript = Join-Path $ProjectDir "start_autopilot.bat"

if ($Action -eq "register") {
    Write-Host "Registering Windows Task: $TaskName..." -ForegroundColor Cyan
    $Trigger = New-ScheduledTaskTrigger -AtStartup
    $ActionCmd = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$BatchScript`"" -WorkingDirectory $ProjectDir
    $Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5)

    Register-ScheduledTask -TaskName $TaskName -Trigger $Trigger -Action $ActionCmd -Principal $Principal -Settings $Settings -Force
    Write-Host "Scheduled task $TaskName successfully registered!" -ForegroundColor Green
    Write-Host "The autopilot will launch automatically at system startup."
} elseif ($Action -eq "unregister") {
    Write-Host "Unregistering Windows Task: $TaskName..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Scheduled task $TaskName unregistered." -ForegroundColor Green
} else {
    Write-Host "Usage: .\setup_autostart_windows.ps1 [-Action register|unregister]"
}
