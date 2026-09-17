"""Does recency-weighted reputation close the trust-then-betray hole? (Closes Reviewer M3.)

[[Stealth Defector]] showed a LIFETIME-average image score is gameable: an invader that
cooperates for K rounds then defects still invades at every timing (+7 to +14 fitness),
because a few late defections barely move a long clean average. This driver re-runs the
identical stealth invader against RECENCY-WEIGHTED reputation modes and asks whether the
exploit disappears:
  * lifetime  : cooperation rate over ALL past rounds        (the original, for reference)
  * window    : cooperation rate over the last W=3 rounds only
  * onestrike : flagged as untrustworthy if it defected in either of its last 2 rounds

Same population as run_stealth (8 agents, 12 rounds, reputation shown, one scripted
invader that plays C for rounds<=K then D). Readout: invasion fitness per (mode,K), and
cooperation TOWARD the invader after it betrays. If recency reputation works, post-betrayal
cooperation toward the invader collapses (like a known defector's ~0.08) and invasion
fitness goes negative.

  python run_recency.py --model haiku --n 8 --rounds 12 --seeds 4 --ks 3,6,9 --modes window,onestrike
"""
import asyncio, csv, os, random, argparse, statistics as st
from civlab.llm import LLM
from civlab.games import reputation as R
from civlab.games.invasion import PAY, pairing

OUT="results/recency"; os.makedirs(OUT,exist_ok=True)

def stealth_move(rnd,K): return "C" if rnd<=K else "D"

async def run_pop(llm, model, mode, K, seed, N, ROUNDS):
    rep_fn=R.REP_MODES[mode]
    rng=random.Random(f"recency-{mode}-K{K}-{seed}")
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
            j=partner.get(i); pm=full[j] if j is not None else []
            r=await llm.ask(R.build_prompt(mem[i], pm, rep_fn), R.SYSTEM, model=model,
                            key=f"{model}-recency-{mode}-K{K}-s{seed}-r{rnd}-a{i}", think=0,
                            tags={"exp":"recency","mode":mode,"K":K,"seed":seed,"round":rnd,"agent":i})
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
    ap.add_argument("--rounds",type=int,default=12); ap.add_argument("--seeds",type=int,default=4)
    ap.add_argument("--ks",default="3,6,9"); ap.add_argument("--modes",default="window,onestrike")
    a=ap.parse_args()
    seeds=list(range(1,a.seeds+1)); Ks=[int(x) for x in a.ks.split(",")]; modes=a.modes.split(",")
    llm=LLM(os.path.join(OUT,"calls.jsonl"), concurrency=int(os.environ.get("CIV_CONC","12")))
    rows=[]
    def checkpoint():
        if rows:
            with open(os.path.join(OUT,"summary.csv"),"w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    async def cell(mode,K,seed):
        d=await run_pop(llm,a.model,mode,K,seed,a.n,a.rounds)
        rows.append(dict(model=a.model,mode=mode,K=K,seed=seed,mean_model_payoff=round(d["mmp"],1),
                         invader_payoff=d["inv"],invasion_fitness=round(d["fit"],1),
                         coop_vs_invader_pre=("" if d["pre"] is None else round(d["pre"],3)),
                         coop_vs_invader_post=("" if d["post"] is None else round(d["post"],3)),
                         exploit_payoff=d["exploit"]))
        checkpoint()
        print(f"{mode} K={K} s{seed}: fit={d['fit']:.0f} pre={d['pre']} post={d['post']} calls={llm.calls} cost=${llm.total_cost:.2f}",flush=True)
    await asyncio.gather(*[cell(m,K,s) for m in modes for K in Ks for s in seeds])
    checkpoint()
    print("DONE recency calls",llm.calls,"cost",round(llm.total_cost,3),"fallbacks",llm.fallback_hits)

if __name__=="__main__": asyncio.run(main())
