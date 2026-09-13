"""One-defector invasion driver: control (all model agents) vs invasion (one scripted AllD).
  python run_invasion.py --model haiku --n 8 --rounds 12 --seeds 4
"""
import asyncio, csv, os, random, argparse, statistics as st
from civlab.llm import LLM
from civlab.games import invasion as V

OUT="results/invasion"; os.makedirs(OUT,exist_ok=True)

async def run_pop(llm, model, cond, seed, N, ROUNDS):
    rng=random.Random(f"{cond}-{seed}")
    invader = (N-1) if cond=="invasion" else None   # last agent is scripted AllD in invasion
    mem={i:[] for i in range(N)}; totals={i:0 for i in range(N)}
    traj=[]
    for rnd in range(1,ROUNDS+1):
        async def decide(i):
            if i==invader: return "D"
            r=await llm.ask(V.build_prompt(mem[i]), V.SYSTEM, model=model,
                            key=f"{model}-{cond}-s{seed}-r{rnd}-a{i}", think=0,
                            tags={"exp":"invasion","cond":cond,"seed":seed,"round":rnd,"agent":i})
            return V.parse_move(r.text)
        moves=await asyncio.gather(*[decide(i) for i in range(N)])
        for a,b in V.pairing(N,rng):
            if b is None: continue
            pa,pb=V.PAY[(moves[a],moves[b])]
            totals[a]+=pa; totals[b]+=pb
            mem[a].append((moves[a],moves[b],pa)); mem[b].append((moves[b],moves[a],pb))
        model_agents=[i for i in range(N) if i!=invader]
        coop=sum(1 for i in model_agents if moves[i]=="C")/len(model_agents)
        traj.append(round(coop,3))
    model_agents=[i for i in range(N) if i!=invader]
    mean_model_pay=st.mean(totals[i] for i in model_agents)
    inv_pay=totals[invader] if invader is not None else None
    return traj, mean_model_pay, inv_pay

async def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--model",default="haiku"); ap.add_argument("--n",type=int,default=8)
    ap.add_argument("--rounds",type=int,default=12); ap.add_argument("--seeds",type=int,default=4)
    a=ap.parse_args(); seeds=list(range(1,a.seeds+1))
    llm=LLM(os.path.join(OUT,"calls.jsonl"), concurrency=8)
    rows=[]; traj_rows=[]
    async def cell(cond,seed):
        traj,mmp,inv=await run_pop(llm,a.model,cond,seed,a.n,a.rounds)
        for t,c in enumerate(traj): traj_rows.append(dict(model=a.model,cond=cond,seed=seed,round=t+1,coop_rate=c))
        rows.append(dict(model=a.model,cond=cond,seed=seed,coop_start=traj[0],coop_end=traj[-1],
                         coop_mean=round(st.mean(traj),3),mean_model_payoff=round(mmp,1),
                         invader_payoff=("" if inv is None else inv),
                         invasion_fitness=("" if inv is None else round(inv-mmp,1))))
        print(f"{cond} s{seed}: coop {traj[0]:.2f}->{traj[-1]:.2f} mean={st.mean(traj):.2f} model_pay={mmp:.0f} invader={inv} calls={llm.calls} cost=${llm.total_cost:.2f}",flush=True)
    conds=["control","invasion"]
    await asyncio.gather(*[cell(c,s) for c in conds for s in seeds])
    with open(os.path.join(OUT,"trajectory.csv"),"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(traj_rows[0].keys())); w.writeheader(); w.writerows(traj_rows)
    with open(os.path.join(OUT,"summary.csv"),"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print("DONE invasion calls",llm.calls,"cost",round(llm.total_cost,3))

if __name__=="__main__": asyncio.run(main())
