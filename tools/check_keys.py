"""Check each provider key WITHOUT revealing it. Prints (and saves to results/_phase0/keys_check.txt):
whether the key is present in this shell, first 4 chars + length, whether it matches the value stored
in Windows user environment variables, obvious formatting problems, and the provider's live answer
(200 OK / 401 rejected / unreachable). Safe to paste the output anywhere.

    python -m tools.check_keys
"""
import os, sys

PROVIDERS = {
    "GROQ_API_KEY":       ("groq",       "https://api.groq.com/openai/v1/models", "gsk_"),
    "GEMINI_API_KEY":     ("gemini",     "https://generativelanguage.googleapis.com/v1beta/openai/models", ""),   # Google issues both AIza… and AQ.… keys
    "MISTRAL_API_KEY":    ("mistral",    "https://api.mistral.ai/v1/models", ""),
    "NVIDIA_API_KEY":     ("nvidia",     "https://integrate.api.nvidia.com/v1/models", "nvapi-"),
    "OPENROUTER_API_KEY": ("openrouter", "https://openrouter.ai/api/v1/models", "sk-or-"),
}

def stored_user_value(name):
    """Value saved by tools\\set_keys.ps1 (HKCU\\Environment); None if unavailable. Never printed."""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
            return winreg.QueryValueEx(k, name)[0]
    except Exception:
        return None

def main():
    import httpx
    lines = []
    for name, (prov, url, prefix) in PROVIDERS.items():
        v = os.environ.get(name, "")
        stored = stored_user_value(name)
        issues = []
        if not v:
            issues.append("not set in this shell" + (" (but saved for your user: open a NEW PowerShell)" if stored else ""))
        else:
            if stored is not None and stored != v: issues.append("differs from the saved value: open a NEW PowerShell")
            if v != v.strip(): issues.append("has leading/trailing spaces")
            if v[:1] in "\"'" or v[-1:] in "\"'": issues.append("has quote characters")
            if "=" in v: issues.append("contains '=' (did you paste NAME=value?)")
            if prefix and not v.startswith(prefix): issues.append(f"expected to start with {prefix!r}")
        live = "-"
        if v:
            try:
                r = httpx.get(url, headers={"Authorization": f"Bearer {v.strip()}"}, timeout=20)
                live = {200: "OK (key accepted)", 401: "401 REJECTED (invalid or revoked key)",
                        403: "403 forbidden (key valid but not allowed; check account/tier)"}.get(r.status_code, f"HTTP {r.status_code}")
            except Exception as e:
                live = f"unreachable: {type(e).__name__}"
        shown = f"{v[:4]}... len={len(v)}" if v else "(none)"
        lines.append(f"{prov:11s} {shown:18s} live: {live:40s} {'; '.join(issues)}")
    out = "\n".join(lines)
    print(out)
    os.makedirs(os.path.join("results", "_phase0"), exist_ok=True)
    open(os.path.join("results", "_phase0", "keys_check.txt"), "w", encoding="utf-8").write(out + "\n")

if __name__ == "__main__":
    sys.exit(main())
