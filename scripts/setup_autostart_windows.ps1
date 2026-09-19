# PowerShell script to register 24/7 AI Instagram Reels Autopilot in Windows Task Scheduler
param (
    [string]$Action = "register"
)

$TaskName = "AI_Instagram_Reels_Autopilot_24x7"
$ProjectDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Definition)
$SilentRunner = Join-Path $ProjectDir "run_autopilot_silent.vbs"

if ($Action -eq "register") {
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host " Registering AI Instagram Reels Autopilot 24/7 Task..." -ForegroundColor Cyan
    Write-Host "==========================================================" -ForegroundColor Cyan

    $Trigger = New-ScheduledTaskTrigger -AtLogOn
    $ActionCmd = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "`"$SilentRunner`"" -WorkingDirectory $ProjectDir
    $Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 5 -RestartInterval (New-TimeSpan -Minutes 2) -ExecutionTimeLimit (New-TimeSpan -Days 365)

    Register-ScheduledTask -TaskName $TaskName -Trigger $Trigger -Action $ActionCmd -Principal $Principal -Settings $Settings -Force

    Write-Host "Task '$TaskName' registered successfully!" -ForegroundColor Green
    Write-Host "The autopilot will automatically launch at system startup / login." -ForegroundColor Green
    Write-Host "Starting the task now in background..." -ForegroundColor Yellow
    Start-ScheduledTask -TaskName $TaskName
    Write-Host "Autopilot is now running silently 24/7 in the background!" -ForegroundColor Green

} elseif ($Action -eq "unregister") {
    Write-Host "Unregistering Task '$TaskName'..." -ForegroundColor Yellow
    Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Task '$TaskName' unregistered." -ForegroundColor Green
} else {
    Write-Host "Usage: .\setup_autostart_windows.ps1 [-Action register|unregister]"
}
