"""Load API keys from the repo's .env without printing them.

Handles a UTF-8 byte-order mark (PowerShell 5's `Set-Content -Encoding utf8` writes one),
Windows line endings, quotes and blank/comment lines. Values go into os.environ only if
not already set there. Nothing here ever logs a value.
"""
import os

def load_env(path=".env"):
    if not os.path.exists(path):
        return []
    loaded = []
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip().lstrip("﻿"); v = v.strip().strip('"').strip("'")
            if not v or "paste_here" in v:
                continue
            os.environ.setdefault(k, v)
            loaded.append(k)
    return loaded

def key_status(names):
    """{name: 'set' | 'missing'} — never returns values."""
    return {n: ("set" if os.environ.get(n) else "missing") for n in names}
