import csv, statistics as st
from collections import defaultdict
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

tr=list(csv.DictReader(open("results/replicator/trajectory.csv")))
# mean defector fraction by (cond,f0,gen)
agg=defaultdict(lambda: defaultdict(list))
for r in tr:
    agg[(r["cond"],int(r["f0"]))][int(r["gen"])].append(float(r["defector_frac"]))
GOOD="#2f9e6f"; BAD="#d1495b"
fig,ax=plt.subplots(1,2,figsize=(12,4.8),sharey=True)
for k,f0 in enumerate([1,3]):
    for cond,color,lab in [("anon",BAD,"anonymous"),("reputation",GOOD,"reputation shown")]:
        d=agg[(cond,f0)]; gens=sorted(d)
        means=[st.mean(d[g]) for g in gens]
        for g in gens:
            for v in d[g]: ax[k].plot(g, v, "o", color=color, alpha=0.18, ms=4)
        ax[k].plot(gens, means, "-", color=color, lw=2.6, label=lab)
    ax[k].axhline(f0/8, ls=":", c="#888", lw=1)
    ax[k].set_title(f"Start: {f0} defector{'s' if f0>1 else ''} of 8  ({f0/8:.0%})")
    ax[k].set_xlabel("generation"); ax[k].set_ylim(-0.05,1.05)
    ax[k].set_xticks(gens)
ax[0].set_ylabel("defector fraction of population")
ax[0].legend(loc="center left", fontsize=10, framealpha=.9)
fig.suptitle("Replicator dynamics: defection invades under anonymity, dies out under reputation",
             fontweight="bold", y=1.02)
plt.tight_layout(); plt.savefig("results/replicator/replicator_figure.png", dpi=120, bbox_inches="tight")
print("wrote results/replicator/replicator_figure.png")

# print aggregate end-state
print("\n=== end-of-run defector fraction (mean of 3 seeds) ===")
for cond in ["anon","reputation"]:
    for f0 in [1,3]:
        d=agg[(cond,f0)]; g=max(d)
        print(f"  {cond:11s} f0={f0}: start {f0/8:.2f} -> end {st.mean(d[g]):.2f}")
