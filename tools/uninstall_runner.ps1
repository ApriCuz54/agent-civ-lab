Unregister-ScheduledTask -TaskName "agent-civ-lab-runner" -Confirm:$false -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName "agent-civ-lab-autosync" -Confirm:$false -ErrorAction SilentlyContinue
Write-Host "Removed agent-civ-lab scheduled tasks."
