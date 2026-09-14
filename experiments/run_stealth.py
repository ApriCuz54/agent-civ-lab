"""Stealth-defector invasion: can a strategic exploiter GAME the reputation defense?

Reputation-enabled population PD (same as run_reputation.py: before each round every
model-agent sees its current partner's public cooperation record / image score). Into it
we drop ONE scripted STEALTH invader that COOPERATES for the first K rounds -- building a
spotless reputation -- then DEFECTS for the rest ("trust, then betray").

We sweep the betrayal round K in {3, 6, 9} over a 12-round horizon. This locates the
optimal trust-then-betray point and tests whether indirect reciprocity (which crushed a
naive AllD in run_reputation: invasion fitness -16, cooperators defect on the known
defector 92% of the time) can be defeated by an invader that only reveals itself once
trusted.

Compare against two arms already collected in results/reputation/summary.csv:
  * control  : no invader (cooperation stable at ~1.0)
  * invasion : naive AllD invader (K=0) -- defects from round 1, gets punished immediately.

Readouts (game theory / evolutionary games):
  * invasion_fitness = invader_payoff - mean model-agent payoff, per K. Positive => the
    stealth strategy is favoured by selection (reputation defense is gameable).
  * coop_vs_invader_pre (rounds <= K) vs coop_vs_invader_post (rounds > K): do peers keep
    cooperating with the invader while its record is clean, and how fast do they cut it off
    once it betrays?
  * exploit_payoff: invader's score earned in the betrayal window (rounds > K) -- the sucker
    payoffs it harvests before its reputation collapses.
  * invader_rep_at_betrayal: invader's public cooperation rate the round it first defects.

  python run_stealth.py --model haiku --n 8 --rounds 12 --seeds 4 --ks 3,6,9
"""
import asyncio, csv, os, random, argparse, statistics as st
from civlab.llm import LLM
from civlab.games import reputation as R
from civlab.games.invasion import PAY, pairing

OUT="results/stealth"; os.makedirs(OUT,exist_ok=True)

def stealth_move(rnd, K):
    """Scripted stealth invader: cooperate through round K, defect after."""
    return "C" if rnd<=K else "D"

async def run_pop(llm, model, K, seed, N, ROUNDS):
    rng=random.Random(f"stealth-K{K}-{seed}")
    invader=N-1
    full={i:[] for i in range(N)}      # each agent's full move history (public reputation)
    mem={i:[] for i in range(N)}       # each agent's own (own,partner,pay) memory
    totals={i:0 for i in range(N)}
    traj=[]                            # model-agents' cooperation rate per round
    # targeting split by betrayal phase (model-agent move vs the invader)
    cvi_pre=[]; cvi_post=[]
    exploit_pay=0                      # invader payoff in rounds > K
    inv_rep_at_betrayal=None
    for rnd in range(1,ROUNDS+1):
        pairs=pairing(N,rng)
        partner={}
        for a,b in pairs:
            if b is None: continue
            partner[a]=b; partner[b]=a
        # snapshot invader's public reputation the round it first betrays
        if rnd==K+1 and inv_rep_at_betrayal is None:
            fm=full[invader]; inv_rep_at_betrayal=(round(fm.count("C")/len(fm),3) if fm else None)
        async def decide(i):
            if i==invader: return stealth_move(rnd,K)
            j=partner.get(i)
            pm = full[j] if j is not None else []
            r=await llm.ask(R.build_prompt(mem[i], pm), R.SYSTEM, model=model,
                            key=f"{model}-stealth-K{K}-s{seed}-r{rnd}-a{i}", think=0,
                            tags={"exp":"stealth","K":K,"seed":seed,"round":rnd,"agent":i})
            return R.parse_move(r.text)
        actors=[i for i in range(N) if i in partner]
        decided=dict(zip(actors, await asyncio.gather(*[decide(i) for i in actors])))
        for a,b in pairs:
            if b is None: continue
            ma,mb=decided[a],decided[b]; pa,pb=PAY[(ma,mb)]
            totals[a]+=pa; totals[b]+=pb
            full[a].append(ma); full[b].append(mb)
            mem[a].append((ma,mb,pa)); mem[b].append((mb,ma,pb))
            if invader in (a,b) and rnd>K:
                exploit_pay += pa if a==invader else pb
            # targeting: a model-agent's move against the invader, split by phase
            for x,mx,partner_of_x in [(a,ma,b),(b,mb,a)]:
                if x==invader: continue
                if partner_of_x==invader:
                    (cvi_pre if rnd<=K else cvi_post).append(1 if mx=="C" else 0)
        model_agents=[i for i in range(N) if i!=invader and i in decided]
        traj.append(round(sum(1 for i in model_agents if decided[i]=="C")/len(model_agents),3))
    model_agents=[i for i in range(N) if i!=invader]
    mmp=st.mean(totals[i] for i in model_agents)
    inv=totals[invader]
    return dict(traj=traj, mmp=mmp, inv=inv,
                cvi_pre=(st.mean(cvi_pre) if cvi_pre else None),
                cvi_post=(st.mean(cvi_post) if cvi_post else None),
                exploit_pay=exploit_pay, inv_rep_at_betrayal=inv_rep_at_betrayal)

async def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--model",default="haiku"); ap.add_argument("--n",type=int,default=8)
    ap.add_argument("--rounds",type=int,default=12); ap.add_argument("--seeds",type=int,default=4)
    ap.add_argument("--ks",default="3,6,9")
    a=ap.parse_args()
    seeds=list(range(1,a.seeds+1)); Ks=[int(x) for x in a.ks.split(",")]
    llm=LLM(os.path.join(OUT,"calls.jsonl"), concurrency=8)
    rows=[]; traj_rows=[]
    async def cell(K,seed):
        d=await run_pop(llm,a.model,K,seed,a.n,a.rounds)
        traj=d["traj"]
        for t,c in enumerate(traj):
            traj_rows.append(dict(model=a.model,K=K,seed=seed,round=t+1,coop_rate=c))
        rows.append(dict(model=a.model,K=K,seed=seed,
                         coop_start=traj[0],coop_end=traj[-1],coop_mean=round(st.mean(traj),3),
                         mean_model_payoff=round(d["mmp"],1),invader_payoff=d["inv"],
                         invasion_fitness=round(d["inv"]-d["mmp"],1),
                         coop_vs_invader_pre=("" if d["cvi_pre"] is None else round(d["cvi_pre"],3)),
                         coop_vs_invader_post=("" if d["cvi_post"] is None else round(d["cvi_post"],3)),
                         exploit_payoff=d["exploit_pay"],
                         invader_rep_at_betrayal=("" if d["inv_rep_at_betrayal"] is None else d["inv_rep_at_betrayal"])))
        print(f"K={K} s{seed}: coop {traj[0]:.2f}->{traj[-1]:.2f} model_pay={d['mmp']:.0f} "
              f"invader={d['inv']} fit={d['inv']-d['mmp']:.0f} C|inv pre={d['cvi_pre']} post={d['cvi_post']} "
              f"calls={llm.calls} cost=${llm.total_cost:.2f}",flush=True)
    await asyncio.gather(*[cell(K,s) for K in Ks for s in seeds])
    rows.sort(key=lambda r:(r["K"],r["seed"]))
    traj_rows.sort(key=lambda r:(r["K"],r["seed"],r["round"]))
    with open(os.path.join(OUT,"trajectory.csv"),"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(traj_rows[0].keys())); w.writeheader(); w.writerows(traj_rows)
    with open(os.path.join(OUT,"summary.csv"),"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print("DONE stealth calls",llm.calls,"cost",round(llm.total_cost,3))

if __name__=="__main__": asyncio.run(main())
