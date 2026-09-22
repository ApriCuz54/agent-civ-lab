import csv, statistics as st
from collections import defaultdict
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

d=defaultdict(list)
for r in csv.DictReader(open("results/recency/summary.csv")):
    d[(r["mode"],int(r["K"]))].append(float(r["invasion_fitness"]))
life={3:10.4,6:13.6,9:7.3}   # from Stealth Defector (lifetime image score)
Ks=[3,6,9]; labels=[f"betray r{K+1}" for K in Ks]
series=[("lifetime average\n(gameable)", [life[K] for K in Ks], "#d1495b"),
        ("recency window\n(last 3)",      [st.mean(d[("window",K)]) for K in Ks], "#e0a13a"),
        ("one-strike\n(last 2)",          [st.mean(d[("onestrike",K)]) for K in Ks], "#2f9e6f")]
import numpy as np
x=np.arange(len(Ks)); w=0.26
fig,ax=plt.subplots(figsize=(9,5.2))
for i,(lab,vals,c) in enumerate(series):
    b=ax.bar(x+(i-1)*w, vals, w, label=lab, color=c)
    for xi,v in zip(x+(i-1)*w, vals):
        ax.text(xi, v+(0.3 if v>=0 else -0.8), f"{v:+.0f}", ha="center", va="bottom" if v>=0 else "top", fontsize=9)
ax.axhline(0, color="k", lw=1)
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set_ylabel("stealth invader's invasion fitness\n(positive = exploit succeeds)")
ax.set_title("Recency-weighted reputation closes the trust-then-betray hole", fontweight="bold")
ax.legend(title="reputation signal", fontsize=9)
ax.set_ylim(-8,16)
plt.tight_layout(); plt.savefig("results/recency/recency_figure.png", dpi=120)
print("wrote results/recency/recency_figure.png")
