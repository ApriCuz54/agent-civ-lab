# Save API keys as Windows *user* environment variables, typed at a hidden prompt.
# Keys never appear on screen, in PowerShell history, or in any file inside the repo,
# so nothing that can see the repo folder (including Claude's folder access) can read them.
#
# Run:  powershell -ExecutionPolicy Bypass -File tools\set_keys.ps1
# Press Enter at a prompt to leave that key unchanged. Open a NEW PowerShell window afterwards.
$names = "GROQ_API_KEY", "GEMINI_API_KEY", "MISTRAL_API_KEY", "NVIDIA_API_KEY", "OPENROUTER_API_KEY"
foreach ($n in $names) {
    $s = Read-Host "Paste $n (Enter to skip)" -AsSecureString
    $b = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($s)
    $v = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($b)
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($b)
    if ($v -and $v.Trim()) {
        [Environment]::SetEnvironmentVariable($n, $v.Trim(), "User")
        Write-Host "  $n saved"
    } else {
        Write-Host "  $n unchanged"
    }
    Remove-Variable v, s
}
Write-Host ""
Write-Host "Done. Close this window and open a NEW PowerShell so the keys are visible."
Write-Host "Check (shows only True/False):"
Write-Host '  python -c "import os; print({k: bool(os.environ.get(k)) for k in [''GROQ_API_KEY'',''GEMINI_API_KEY'',''MISTRAL_API_KEY'',''NVIDIA_API_KEY'',''OPENROUTER_API_KEY'']})"'
