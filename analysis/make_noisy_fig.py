import csv, statistics as st
from collections import defaultdict
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
d=defaultdict(list)
for r in csv.DictReader(open("results/noisy/summary.csv")):
    key=("forge" if r["cond"]=="forge" else r["eps"])
    d[key].append(float(r["invasion_fitness"]))
order=[("0.0","noise ε=0"),("0.15","noise ε=.15"),("0.3","noise ε=.30"),("0.5","noise ε=.50"),("forge","forgeable")]
labs=[l for _,l in order]; vals=[st.mean(d[k]) for k,_ in order]
GOOD="#2f9e6f"; BAD="#d1495b"
cols=[GOOD,GOOD,GOOD,GOOD,BAD]
fig,ax=plt.subplots(figsize=(9,5.2))
x=range(len(order))
ax.bar(x,vals,color=cols)
for i,v in enumerate(vals):
    ax.text(i,v+(0.4 if v>=0 else -0.9),f"{v:+.1f}",ha="center",va="bottom" if v>=0 else "top",fontweight="bold",fontsize=10)
ax.axhline(0,color="#444",lw=1)
ax.axhline(14,ls=":",c=BAD,lw=1.4); ax.text(0.05,14.4,"lifetime-average (gameable) level ≈ +14",color=BAD,fontsize=9)
ax.set_xticks(list(x)); ax.set_xticklabels(labs)
ax.set_ylabel("stealth invader's invasion fitness\n(0 = recency defense holds; higher = exploit succeeds)")
ax.set_title("Recency reputation is robust to noise, but forgery breaks it",fontweight="bold")
ax.set_ylim(-6,17)
ax.text(1.5,-4.5,"observation noise (symmetric): defense holds",ha="center",color=GOOD,fontsize=9)
plt.tight_layout(); plt.savefig("results/noisy/noisy_figure.png",dpi=120)
print("wrote results/noisy/noisy_figure.png")
