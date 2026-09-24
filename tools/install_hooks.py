"""Install a git pre-commit hook that blocks commits containing API-key-looking strings.
    python -m tools.install_hooks
"""
import os, stat
HOOK = r'''#!/bin/sh
# agent-civ-lab: refuse to commit anything that looks like an API key
if git diff --cached -U0 | grep -E '^\+' | grep -E -q '(gsk_[A-Za-z0-9]{20,}|sk-or-v1-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}|nvapi-[A-Za-z0-9_-]{20,}|sk-ant-[A-Za-z0-9_-]{20,})'; then
  echo "BLOCKED: staged changes contain what looks like an API key. Remove it (keys belong only in .env)." >&2
  exit 1
fi
if git diff --cached --name-only | grep -E -q '(^|/)\.env$'; then
  echo "BLOCKED: .env must never be committed." >&2; exit 1
fi
'''
def main():
    p = os.path.join(".git", "hooks", "pre-commit")
    open(p, "w", newline="\n").write(HOOK)
    os.chmod(p, os.stat(p).st_mode | stat.S_IEXEC)
    print("Installed", p)
if __name__ == "__main__":
    main()
