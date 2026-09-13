"""Regenerate the summary figures from the committed results/*_summary.csv files.
Usage:  python -m analysis.make_figures   (from the repo root)
No API calls; pure plotting."""
import csv, os, statistics as st, random
from collections import defaultdict
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

RES = "results"; random.seed(0)
def ci95(v):
    if len(set(v)) < 2: return (st.mean(v), st.mean(v))
    bs = sorted(st.mean([random.choice(v) for _ in v]) for _ in range(3000)); return bs[75], bs[2925]

def collusion_defection():
    pr = defaultdict(list)
    for r in csv.DictReader(open(f"{RES}/pricing_summary.csv")): pr[r["interv"]].append(float(r["collusion_index"]))
    ip = defaultdict(list)
    for r in csv.DictReader(open(f"{RES}/ipd_summary.csv")): ip[r["interv"]].append(float(r["coop_rate"]))
    op_pr = sorted(pr, key=lambda k: -st.mean(pr[k])); op_ip = sorted(ip, key=lambda k: st.mean(ip[k]))
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    base = st.mean(pr["control"])
    ax[0].barh(op_pr, [st.mean(pr[k]) for k in op_pr],
               color=["#d1495b" if st.mean(pr[k]) > base + 0.03 else ("#4c78a8" if k == "control" else "#54a24b") for k in op_pr])
    ax[0].axvline(base, ls="--", c="gray", lw=1); ax[0].invert_yaxis()
    ax[0].set_title("Collusion by prompt phrase (0=competitive, 1=monopoly)"); ax[0].set_xlabel("collusion index")
    ax[1].barh(op_ip, [st.mean(ip[k]) for k in op_ip],
               color=["#d1495b" if st.mean(ip[k]) < 0.9 else "#54a24b" for k in op_ip])
    ax[1].invert_yaxis(); ax[1].set_xlim(0, 1.05)
    ax[1].set_title("Cooperation by prompt phrase (IPD, baseline=1.0)"); ax[1].set_xlabel("cooperation rate")
    plt.tight_layout(); plt.savefig(f"{RES}/collusion_defection_figure.png", dpi=110); print("wrote collusion_defection_figure.png")

if __name__ == "__main__":
    collusion_defection()
