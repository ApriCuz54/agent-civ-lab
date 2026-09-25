# Commit and push everything that changed in the repo (results, notes, code agents wrote).
# Safety: .gitignore keeps caches/logs/keys out; the pre-commit hook blocks key-like strings;
# never force-pushes; if a push conflicts it rebases once and otherwise gives up and logs.
$ErrorActionPreference = "Continue"
Set-Location (Resolve-Path "$PSScriptRoot\..")
New-Item -ItemType Directory -Force "results\_runner" | Out-Null
$log = "results\_runner\autosync.log"
function Log($m) { "$(Get-Date -Format s) $m" | Add-Content $log }
if (Test-Path ".git\index.lock") {
    $age = (Get-Date) - (Get-Item ".git\index.lock").LastWriteTime
    if ($age.TotalMinutes -gt 10) { Remove-Item ".git\index.lock" -Force; Log "removed stale index.lock" }
    else { Log "git busy (index.lock); skipping"; exit 0 }
}
git add -A 2>&1 | Out-Null
git diff --cached --quiet
if ($LASTEXITCODE -eq 0) { Log "nothing to commit"; exit 0 }
$msg = "autosync: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
git commit -q -m $msg -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -m "Claude-Session: https://claude.ai/code/session_01TYdxsR3q6NvyC7CfjSdqX8" 2>&1 | Add-Content $log
if ($LASTEXITCODE -ne 0) { Log "COMMIT BLOCKED (see above; likely the key-scan hook) - an agent must investigate"; exit 1 }
git push -q 2>&1 | Add-Content $log
if ($LASTEXITCODE -ne 0) {
    git pull --rebase -q 2>&1 | Add-Content $log
    git push -q 2>&1 | Add-Content $log
    if ($LASTEXITCODE -ne 0) { Log "PUSH FAILED after rebase - an agent must investigate"; exit 1 }
}
Log "pushed: $msg"
