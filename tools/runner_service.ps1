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
function Run-WithTimeout($argsList, $outFile, $seconds) {
    # Runs python with a hard wall-clock limit so one hung provider can never block the runner.
    $p = Start-Process -FilePath $Python -ArgumentList $argsList -NoNewWindow -PassThru `
         -RedirectStandardOutput $outFile -RedirectStandardError "$outFile.err"
    if (-not $p.WaitForExit($seconds * 1000)) {
        Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
        "$(Get-Date -Format s) TIMEOUT after $seconds s: $argsList" | Add-Content $svc
    }
}
if (Test-Path "results\_runner\REQUEST_PHASE0") {
    Remove-Item "results\_runner\REQUEST_PHASE0" -Force
    "$(Get-Date -Format s) REQUEST_PHASE0" | Add-Content $svc
    Run-WithTimeout "-m tools.discover_models" "results\_runner\phase0_discover.txt" 300
    Run-WithTimeout "-m tools.bench_local"     "results\_runner\phase0_bench.txt"    1200
    Run-WithTimeout "-m tools.smoke"           "results\_runner\phase0_smoke.txt"    3600
    "$(Get-Date -Format s) REQUEST_PHASE0 done" | Add-Content $svc
}
if (Test-Path "results\_runner\REQUEST_TESTS") {
    Remove-Item "results\_runner\REQUEST_TESTS" -Force
    Run-WithTimeout "-m pytest -q tests" "results\_runner\tests.txt" 900
    "$(Get-Date -Format s) REQUEST_TESTS exit $LASTEXITCODE" | Add-Content $svc
}
& $Python -m tools.run_queue 2>&1 | Out-Null
"$(Get-Date -Format s) runner exit code $LASTEXITCODE" | Add-Content $svc
& powershell -NoProfile -ExecutionPolicy Bypass -File "$PSScriptRoot\autosync.ps1"
