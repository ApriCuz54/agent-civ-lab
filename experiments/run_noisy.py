"""Noisy & forgeable reputation — does the recency defense survive imperfect signals?
(Completes Reviewer M3: the recency/one-strike fix in run_recency.py used a truthful,
perfectly-observed image score. Real reputation is noisy, partial, and spoofable.)

Setup = run_recency's winning defense: recency-weighted image score (cooperation over the
partner's last W=3 rounds), same population PD (8 agents, 12 rounds), and the same stealth
invader that cooperates through round K then defects. K is fixed at 6 — the mid-game
betrayal that a *clean* recency signal fully neutralised (invasion fitness ~0). We now
degrade the signal and ask whether the exploit reopens:

  * noise eps : each move in the observed window is independently FLIPPED with probability
                eps before the observer computes the reputation (symmetric observation noise,
                applied to every partner). Sweep eps in {0.0, 0.15, 0.30, 0.50}.
  * forge     : the invader SPOOFS a clean record — whenever a peer looks up the invader's
                reputation it sees an all-cooperate window, regardless of what it actually did.
                All honest partners are observed truthfully (eps=0).

Readout: invasion fitness (invader − mean peer) and cooperation TOWARD the invader after it
betrays. eps=0 reproduces the recency baseline (exploit closed, fitness ~0). If fitness
climbs back toward the lifetime-average level (~+14) as eps rises, the defense is fragile to
noise; forge tests the worst case.

  python run_noisy.py --model haiku --n 8 --rounds 12 --seeds 3 --k 6 --eps 0,0.15,0.3,0.5
"""
import asyncio, csv, os, random, argparse, statistics as st
from civlab.llm import LLM
from civlab.games import reputation as R
from civlab.games.invasion import PAY, pairing

OUT="results/noisy"; os.makedirs(OUT,exist_ok=True)
W=3  # recency window (matches run_recency "window" mode)

def stealth_move(rnd,K): return "C" if rnd<=K else "D"

def observe(actual_window, eps, rng):
    """Return the observer's (possibly corrupted) view of a partner's recent moves."""
    if eps<=0: return list(actual_window)
    return [("D" if m=="C" else "C") if rng.random()<eps else m for m in actual_window]

async def run_pop(llm, model, cond, eps, K, seed, N, ROUNDS):
    rng=random.Random(f"noisy-{cond}-{eps}-K{K}-{seed}")
    invader=N-1
    full={i:[] for i in range(N)}; mem={i:[] for i in range(N)}; totals={i:0 for i in range(N)}
    cvi_pre=[]; cvi_post=[]; exploit=0
    for rnd in range(1,ROUNDS+1):
        pairs=pairing(N,rng); partner={}
        for a,b in pairs:
            if b is None: continue
            partner[a]=b; partner[b]=a
        async def decide(i):
            if i==invader: return stealth_move(rnd,K)
            j=partner.get(i)
            if j is None:
                shown=[]
            elif cond=="forge" and j==invader:
                shown=["C"]*min(W,max(1,len(full[j])))   # invader forges a clean recent record
            else:
                shown=observe(full[j][-W:], eps, rng)     # honest recency view, corrupted by noise eps
            r=await llm.ask(R.build_prompt(mem[i], shown, R.reputation_str_window), R.SYSTEM, model=model,
                            key=f"{model}-noisy-{cond}-e{eps}-K{K}-s{seed}-r{rnd}-a{i}", think=0,
                            tags={"exp":"noisy","cond":cond,"eps":eps,"K":K,"seed":seed,"round":rnd,"agent":i})
            return R.parse_move(r.text)
        actors=[i for i in range(N) if i in partner]
        decided=dict(zip(actors, await asyncio.gather(*[decide(i) for i in actors])))
        for a,b in pairs:
            if b is None: continue
            ma,mb=decided[a],decided[b]; pa,pb=PAY[(ma,mb)]
            totals[a]+=pa; totals[b]+=pb
            full[a].append(ma); full[b].append(mb); mem[a].append((ma,mb,pa)); mem[b].append((mb,ma,pb))
            if invader in (a,b) and rnd>K: exploit += pa if a==invader else pb
            for x,mx,pox in [(a,ma,b),(b,mb,a)]:
                if x==invader: continue
                if pox==invader: (cvi_pre if rnd<=K else cvi_post).append(1 if mx=="C" else 0)
    ma_=[i for i in range(N) if i!=invader]; mmp=st.mean(totals[i] for i in ma_); inv=totals[invader]
    return dict(mmp=mmp,inv=inv,fit=inv-mmp,
                pre=(st.mean(cvi_pre) if cvi_pre else None),post=(st.mean(cvi_post) if cvi_post else None),exploit=exploit)

async def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--model",default="haiku"); ap.add_argument("--n",type=int,default=8)
    ap.add_argument("--rounds",type=int,default=12); ap.add_argument("--seeds",type=int,default=3)
    ap.add_argument("--k",type=int,default=6); ap.add_argument("--eps",default="0,0.15,0.3,0.5")
    a=ap.parse_args()
    seeds=list(range(1,a.seeds+1)); epslist=[float(x) for x in a.eps.split(",")]
    llm=LLM(os.path.join(OUT,"calls.jsonl"), concurrency=int(os.environ.get("CIV_CONC","12")))
    rows=[]
    def checkpoint():
        if rows:
            with open(os.path.join(OUT,"summary.csv"),"w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    async def cell(cond,eps,seed):
        d=await run_pop(llm,a.model,cond,eps,a.k,seed,a.n,a.rounds)
        rows.append(dict(model=a.model,cond=cond,eps=eps,K=a.k,seed=seed,
                         mean_model_payoff=round(d["mmp"],1),invader_payoff=d["inv"],
                         invasion_fitness=round(d["fit"],1),
                         coop_vs_invader_post=("" if d["post"] is None else round(d["post"],3)),
                         exploit_payoff=d["exploit"]))
        checkpoint()
        print(f"{cond} eps={eps} s{seed}: fit={d['fit']:.0f} post={d['post']} calls={llm.calls} cost=${llm.total_cost:.2f}",flush=True)
    # build cell list: noise sweep + one forge condition (eps ignored for forge)
    cells=[("noise",e,s) for e in epslist for s in seeds]+[("forge",0.0,s) for s in seeds]
    await asyncio.gather(*[cell(c,e,s) for (c,e,s) in cells])
    checkpoint()
    print("DONE noisy calls",llm.calls,"cost",round(llm.total_cost,3),"fallbacks",llm.fallback_hits)

if __name__=="__main__": asyncio.run(main())
