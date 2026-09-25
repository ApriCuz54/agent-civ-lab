import csv, json, os
PHASE0 = os.path.join("results", "_phase0")
def ensure(p=PHASE0):
    os.makedirs(p, exist_ok=True); return p
def write_csv(path, rows):
    if not rows: return
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
def print_table(rows, cols):
    if not rows:
        print("  (no rows)"); return
    widths = {c: max(len(c), *(len(str(r.get(c, ""))) for r in rows)) for c in cols}
    print("  ".join(c.ljust(widths[c]) for c in cols))
    for r in rows: print("  ".join(str(r.get(c, "")).ljust(widths[c]) for c in cols))
