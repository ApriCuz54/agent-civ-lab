# What the "agent-civ-lab-runner" scheduled task runs every 15 minutes.
# Starts the queue runner (a no-op if nothing is pending, PAUSE is set, or it is already running),
# then syncs results to GitHub. Logs: results\_runner\service.log and runner.log (not committed).
param([string]$Python = "python")
$ErrorActionPreference = "Continue"
Set-Location (Resolve-Path "$PSScriptRoot\..")
New-Item -ItemType Directory -Force "results\_runner" | Out-Null
$svc = "results\_runner\service.log"
"$(Get-Date -Format s) service start (python=$Python)" | Add-Content $svc
# Agent requests (flag files an agent creates from any environment with repo access; consumed here):
#   REQUEST_PHASE0 -> re-run discovery, local benchmark and smoke test (gate G0 inputs)
#   REQUEST_TESTS  -> run the offline test suite on this machine, output to results\_runner\tests.txt
if (Test-Path "results\_runner\REQUEST_PHASE0") {
    Remove-Item "results\_runner\REQUEST_PHASE0" -Force
    "$(Get-Date -Format s) REQUEST_PHASE0" | Add-Content $svc
    & $Python -m tools.discover_models *> "results\_runner\phase0_discover.txt"
    & $Python -m tools.bench_local     *> "results\_runner\phase0_bench.txt"
    & $Python -m tools.smoke           *> "results\_runner\phase0_smoke.txt"
}
if (Test-Path "results\_runner\REQUEST_TESTS") {
    Remove-Item "results\_runner\REQUEST_TESTS" -Force
    & $Python -m pytest -q tests *> "results\_runner\tests.txt"
    "$(Get-Date -Format s) REQUEST_TESTS exit $LASTEXITCODE" | Add-Content $svc
}
& $Python -m tools.run_queue 2>&1 | Out-Null
"$(Get-Date -Format s) runner exit code $LASTEXITCODE" | Add-Content $svc
& powershell -NoProfile -ExecutionPolicy Bypass -File "$PSScriptRoot\autosync.ps1"
