"""Reputation-enabled invasion driver: control vs one scripted AllD, with each agent shown
its partner's public cooperation record before choosing. Compares to the no-reputation
invasion (results/invasion). 
  python run_reputation.py --model haiku --n 8 --rounds 12 --seeds 4
"""
import asyncio, csv, os, random, argparse, statistics as st
from civlab.llm import LLM
from civlab.games import reputation as R
from civlab.games.invasion import PAY, pairing

OUT="results/reputation"; os.makedirs(OUT,exist_ok=True)

async def run_pop(llm, model, cond, seed, N, ROUNDS):
    rng=random.Random(f"rep-{cond}-{seed}")
    invader=(N-1) if cond=="invasion" else None
    full={i:[] for i in range(N)}      # each agent's full move history (public reputation)
    mem={i:[] for i in range(N)}       # each agent's own (own,partner,pay) memory
    totals={i:0 for i in range(N)}
    traj=[]; tgt_def=[]; tgt_coop=[]   # targeting: model-agent moves vs defector / vs cooperator
    for rnd in range(1,ROUNDS+1):
        pairs=pairing(N,rng)
        partner={}
        for a,b in pairs:
            if b is None: continue
            partner[a]=b; partner[b]=a
        async def decide(i):
            if i==invader: return "D"
            j=partner.get(i)
            pm = full[j] if j is not None else []
            r=await llm.ask(R.build_prompt(mem[i], pm), R.SYSTEM, model=model,
                            key=f"{model}-rep-{cond}-s{seed}-r{rnd}-a{i}", think=0,
                            tags={"exp":"reputation","cond":cond,"seed":seed,"round":rnd,"agent":i})
            return R.parse_move(r.text)
        actors=[i for i in range(N) if i in partner]
        decided=dict(zip(actors, await asyncio.gather(*[decide(i) for i in actors])))
        # resolve
        for a,b in pairs:
            if b is None: continue
            ma,mb=decided[a],decided[b]; pa,pb=PAY[(ma,mb)]
            totals[a]+=pa; totals[b]+=pb
            full[a].append(ma); full[b].append(mb)
            mem[a].append((ma,mb,pa)); mem[b].append((mb,ma,pb))
            # targeting from the model agents' perspective
            for x,mx,px_partner in [(a,ma,b),(b,mb,a)]:
                if x==invader: continue
                if px_partner==invader: tgt_def.append(1 if mx=="C" else 0)
                else: tgt_coop.append(1 if mx=="C" else 0)
        model_agents=[i for i in range(N) if i!=invader and i in decided]
        traj.append(round(sum(1 for i in model_agents if decided[i]=="C")/len(model_agents),3))
    model_agents=[i for i in range(N) if i!=invader]
    mmp=st.mean(totals[i] for i in model_agents)
    inv=totals[invader] if invader is not None else None
    coop_vs_def = (st.mean(tgt_def) if tgt_def else None)
    coop_vs_coop= (st.mean(tgt_coop) if tgt_coop else None)
    return traj, mmp, inv, coop_vs_def, coop_vs_coop

async def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--model",default="haiku"); ap.add_argument("--n",type=int,default=8)
    ap.add_argument("--rounds",type=int,default=12); ap.add_argument("--seeds",type=int,default=4)
    a=ap.parse_args(); seeds=list(range(1,a.seeds+1))
    llm=LLM(os.path.join(OUT,"calls.jsonl"), concurrency=8)
    rows=[]; traj_rows=[]
    async def cell(cond,seed):
        traj,mmp,inv,cvd,cvc=await run_pop(llm,a.model,cond,seed,a.n,a.rounds)
        for t,c in enumerate(traj): traj_rows.append(dict(model=a.model,cond=cond,seed=seed,round=t+1,coop_rate=c))
        rows.append(dict(model=a.model,cond=cond,seed=seed,coop_start=traj[0],coop_end=traj[-1],
                         coop_mean=round(st.mean(traj),3),mean_model_payoff=round(mmp,1),
                         invader_payoff=("" if inv is None else inv),
                         invasion_fitness=("" if inv is None else round(inv-mmp,1)),
                         coop_vs_defector=("" if cvd is None else round(cvd,3)),
                         coop_vs_cooperator=("" if cvc is None else round(cvc,3))))
        print(f"{cond} s{seed}: coop {traj[0]:.2f}->{traj[-1]:.2f} model_pay={mmp:.0f} invader={inv} "
              f"C|def={cvd} C|coop={cvc} calls={llm.calls} cost=${llm.total_cost:.2f}",flush=True)
    await asyncio.gather(*[cell(c,s) for c in ["control","invasion"] for s in seeds])
    with open(os.path.join(OUT,"trajectory.csv"),"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(traj_rows[0].keys())); w.writeheader(); w.writerows(traj_rows)
    with open(os.path.join(OUT,"summary.csv"),"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print("DONE reputation calls",llm.calls,"cost",round(llm.total_cost,3))

if __name__=="__main__": asyncio.run(main())
