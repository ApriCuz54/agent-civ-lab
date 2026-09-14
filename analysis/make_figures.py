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

def game_theory():
    import csv, statistics as st
    from collections import defaultdict
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    RES="results"
    rows=[r for r in csv.DictReader(open(f"{RES}/progression_summary.csv"))]
    opps=["AllC","TFT","GRIM","Random","AllD"]
    def agg(o,f):
        v=[float(r[f]) for r in rows if r["opp"]==o and r[f] not in ("","None")]
        return st.mean(v) if v else float("nan")
    fig,ax=plt.subplots(1,2,figsize=(12,4.6))
    coops=[agg(o,"coop_rate") for o in opps]
    ax[0].bar(opps,coops,color=["#54a24b" if c>=.8 else ("#d1495b" if c<.3 else "#e0b341") for c in coops])
    ax[0].set_ylim(0,1.05); ax[0].set_title("PD panel: cooperation vs fixed strategies"); ax[0].set_ylabel("cooperation")
    tr=[r for r in csv.DictReader(open(f"{RES}/invasion_trajectory.csv"))]
    byrc=defaultdict(lambda:defaultdict(list))
    for r in tr: byrc[r["cond"]][int(r["round"])].append(float(r["coop_rate"]))
    for cond,c in [("control","#4c78a8"),("invasion","#d1495b")]:
        xs=sorted(byrc[cond]); ax[1].plot(xs,[st.mean(byrc[cond][x]) for x in xs],marker="o",ms=4,label=cond,color=c)
    ax[1].set_ylim(0,1.05); ax[1].set_title("One-defector invasion"); ax[1].set_xlabel("round"); ax[1].legend()
    plt.tight_layout(); plt.savefig(f"{RES}/gametheory_figure.png",dpi=110); print("wrote gametheory_figure.png")

if __name__ == "__main__":
    game_theory()

def reputation():
    import csv, statistics as st
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    RES="results"
    def inv(p): return [r for r in csv.DictReader(open(p)) if r["cond"]=="invasion"]
    nr=inv(f"{RES}/invasion_summary.csv"); rp=inv(f"{RES}/reputation_summary.csv")
    nf=st.mean(float(r["invasion_fitness"]) for r in nr); rf=st.mean(float(r["invasion_fitness"]) for r in rp)
    cvd=st.mean(float(r["coop_vs_defector"]) for r in rp); cvc=st.mean(float(r["coop_vs_cooperator"]) for r in rp)
    fig,ax=plt.subplots(1,2,figsize=(12,4.6))
    ax[0].bar(["no reputation","with reputation"],[nf,rf],color=["#d1495b","#54a24b"]); ax[0].axhline(0,color="k",lw=1)
    ax[0].set_title("Reputation flips the defector's advantage"); ax[0].set_ylabel("invasion fitness")
    ax[1].bar(["toward a\ncooperator","toward the\ndefector"],[cvc,cvd],color=["#4c78a8","#d1495b"]); ax[1].set_ylim(0,1.05)
    ax[1].set_title("With reputation, cooperators target the defector"); ax[1].set_ylabel("cooperation rate")
    plt.tight_layout(); plt.savefig(f"{RES}/reputation_figure.png",dpi=110); print("wrote reputation_figure.png")

if __name__ == "__main__":
    reputation()

def stealth():
    """Trust-then-betray invader vs the reputation defense. Left: invasion fitness by
    betrayal timing (naive AllD K=0 from reputation_summary, then stealth K=3,6,9).
    Right: cooperation TOWARD the invader, pre- vs post-betrayal, next to the 0.08
    targeting a *known* defector receives -- the exploit the slow-decaying image score allows."""
    import csv, statistics as st
    from collections import defaultdict
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    RES="results"
    rp=[r for r in csv.DictReader(open(f"{RES}/reputation_summary.csv")) if r["cond"]=="invasion"]
    alld_fit=st.mean(float(r["invasion_fitness"]) for r in rp)
    known_def=st.mean(float(r["coop_vs_defector"]) for r in rp)   # cooperation a lifelong defector gets (~0.08)
    sr=defaultdict(list)
    for r in csv.DictReader(open(f"{RES}/stealth_summary.csv")): sr[int(r["K"])].append(r)
    Ks=sorted(sr)
    fit=[st.mean(float(r["invasion_fitness"]) for r in sr[K]) for K in Ks]
    pre=[st.mean(float(r["coop_vs_invader_pre"]) for r in sr[K]) for K in Ks]
    post=[st.mean(float(r["coop_vs_invader_post"]) for r in sr[K]) for K in Ks]
    fig,ax=plt.subplots(1,2,figsize=(12,4.6))
    labels=["naive AllD\n(betray r1)"]+[f"stealth\n(betray r{K+1})" for K in Ks]
    vals=[alld_fit]+fit
    ax[0].bar(labels,vals,color=["#d1495b"]+["#54a24b" if v>0 else "#d1495b" for v in fit])
    ax[0].axhline(0,color="k",lw=1)
    peak=Ks[fit.index(max(fit))]
    ax[0].set_title(f"Trust-then-betray beats the reputation defense (peak: betray r{peak+1})")
    ax[0].set_ylabel("invasion fitness (invader − mean peer)")
    x=range(len(Ks)); w=0.38
    ax[1].bar([i-w/2 for i in x],pre,w,label="before betrayal",color="#4c78a8")
    ax[1].bar([i+w/2 for i in x],post,w,label="after betrayal",color="#e0b341")
    ax[1].axhline(known_def,ls="--",c="#d1495b",lw=1.5,label=f"a KNOWN defector gets ({known_def:.2f})")
    ax[1].set_xticks(list(x)); ax[1].set_xticklabels([f"betray r{K+1}" for K in Ks])
    ax[1].set_ylim(0,1.05); ax[1].set_ylabel("cooperation TOWARD the invader")
    ax[1].set_title("Peers never cut off a clean-record exploiter"); ax[1].legend(fontsize=8)
    plt.tight_layout(); plt.savefig(f"{RES}/stealth_figure.png",dpi=110); print("wrote stealth_figure.png")

if __name__ == "__main__":
    stealth()
