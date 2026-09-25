# One-time: register two Windows scheduled tasks for the current user (no admin needed).
#   agent-civ-lab-runner   every 15 min: run the queue (skips if already running), then autosync
#   agent-civ-lab-autosync every 2 h:   commit + push whatever changed (results mid-run, agent notes)
# Run:  powershell -ExecutionPolicy Bypass -File tools\install_runner.ps1
# Remove: powershell -ExecutionPolicy Bypass -File tools\uninstall_runner.ps1
param([int]$EveryMinutes = 15, [int]$SyncHours = 2)
$repo = (Resolve-Path "$PSScriptRoot\..").Path
$py = (Get-Command python -ErrorAction Stop).Source
$ps = "powershell.exe"
$set = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable `
        -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Days 3)
$far = New-TimeSpan -Days 3650

$a1 = New-ScheduledTaskAction -Execute $ps -WorkingDirectory $repo `
      -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$repo\tools\runner_service.ps1`" -Python `"$py`""
$t1 = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes $EveryMinutes) -RepetitionDuration $far
Register-ScheduledTask -TaskName "agent-civ-lab-runner" -Action $a1 -Trigger $t1 -Settings $set -Force | Out-Null

$a2 = New-ScheduledTaskAction -Execute $ps -WorkingDirectory $repo `
      -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$repo\tools\autosync.ps1`""
$t2 = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(30) -RepetitionInterval (New-TimeSpan -Hours $SyncHours) -RepetitionDuration $far
Register-ScheduledTask -TaskName "agent-civ-lab-autosync" -Action $a2 -Trigger $t2 -Settings $set -Force | Out-Null

Write-Host "Installed: agent-civ-lab-runner (every $EveryMinutes min) and agent-civ-lab-autosync (every $SyncHours h)."
Write-Host "Python: $py"
Write-Host "Pause anytime:  New-Item results\_runner\PAUSE      Resume: Remove-Item results\_runner\PAUSE"
