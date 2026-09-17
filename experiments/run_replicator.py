"""Replicator / imitation dynamics — a real evolutionary-stability test (closes Reviewer C2).

The invasion/reputation/stealth experiments were single-episode payoff snapshots; calling
their result "ESS" was an overclaim. Here we actually let strategies REPRODUCE.

Setup. A population of N agents, each carrying a STRATEGY = which system prompt it runs:
  * type C ("cooperator disposition"): a Haiku agent under the neutral group-PD prompt.
  * type D ("defector"): always plays D (scripted).
Each GENERATION the agents play R rounds of randomly-paired PD; an agent's fitness is its
total payoff that generation. Then an imitation update (copy-the-richer / Moran death-birth):
each agent looks at one random peer and, if that peer did better, adopts the peer's strategy
with probability proportional to the payoff gap. We track the DEFECTOR FRACTION across
generations. Rising from a small seed = defection invades (cooperation is NOT an ESS);
falling = cooperation resists invasion (approximately an ESS).

Two conditions test the mechanism the earlier runs implied but never dynamically showed:
  * anon       : agents see only their own recent history (as in One-Defector Invasion).
  * reputation : before each choice an agent sees its partner's public cooperation record
                 (as in Reputation-Enabled Invasion), so cooperators can refuse a known defector.

Sweep the initial defector count f0 to probe the invasion threshold. think=0 throughout.

  python run_replicator.py --model haiku --n 8 --gens 8 --rounds 2 --seeds 3 --f0 1,3
"""
import asyncio, csv, os, random, argparse, statistics as st
from civlab.llm import LLM
from civlab.games.invasion import PAY, pairing
from civlab.games import invasion as INV
from civlab.games import reputation as REP

OUT="results/replicator"; os.makedirs(OUT,exist_ok=True)
MAXPAY=5  # max single-round payoff, for normalising imitation probability

async def run_pop(llm, model, cond, f0, seed, N, GENS, R):
    rng=random.Random(f"rep-{cond}-{f0}-{seed}")
    types=["C"]*N
    for i in rng.sample(range(N), f0): types[i]="D"   # seed f0 defectors
    full={i:[] for i in range(N)}        # public move history (for reputation)
    mem={i:[] for i in range(N)}         # own (own,partner,pay) memory
    traj=[round(sum(t=="D" for t in types)/N,3)]      # defector fraction per generation (gen 0 = initial)
    for g in range(1,GENS+1):
        fit=[0.0]*N
        for _ in range(R):
            pairs=pairing(N,rng); partner={}
            for a,b in pairs:
                if b is None: continue
                partner[a]=b; partner[b]=a
            async def decide(i):
                if types[i]=="D": return "D"
                j=partner.get(i)
                if cond=="reputation":
                    pm = full[j] if j is not None else []
                    r=await llm.ask(REP.build_prompt(mem[i], pm), REP.SYSTEM, model=model,
                                    key=f"{model}-repl-{cond}-f{f0}-s{seed}-g{g}-r{_}-a{i}", think=0,
                                    tags={"exp":"replicator","cond":cond,"f0":f0,"seed":seed,"gen":g,"agent":i})
                else:
                    r=await llm.ask(INV.build_prompt(mem[i]), INV.SYSTEM, model=model,
                                    key=f"{model}-repl-{cond}-f{f0}-s{seed}-g{g}-r{_}-a{i}", think=0,
                                    tags={"exp":"replicator","cond":cond,"f0":f0,"seed":seed,"gen":g,"agent":i})
                return REP.parse_move(r.text)
            actors=[i for i in range(N) if i in partner]
            decided=dict(zip(actors, await asyncio.gather(*[decide(i) for i in actors])))
            for a,b in pairs:
                if b is None: continue
                ma,mb=decided[a],decided[b]; pa,pb=PAY[(ma,mb)]
                fit[a]+=pa; fit[b]+=pb
                full[a].append(ma); full[b].append(mb)
                mem[a].append((ma,mb,pa)); mem[b].append((mb,ma,pb))
        # imitation update (synchronous copy-the-richer / Moran)
        new=list(types)
        for i in range(N):
            j=rng.randrange(N)
            if j!=i and fit[j]>fit[i]:
                p=(fit[j]-fit[i])/(R*MAXPAY)   # normalised payoff gap in [0,1]
                if rng.random()<p: new[i]=types[j]
        types=new
        traj.append(round(sum(t=="D" for t in types)/N,3))
    return traj

async def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--model",default="haiku"); ap.add_argument("--n",type=int,default=8)
    ap.add_argument("--gens",type=int,default=8); ap.add_argument("--rounds",type=int,default=2)
    ap.add_argument("--seeds",type=int,default=3); ap.add_argument("--f0",default="1,3")
    a=ap.parse_args()
    seeds=list(range(1,a.seeds+1)); F0=[int(x) for x in a.f0.split(",")]
    llm=LLM(os.path.join(OUT,"calls.jsonl"), concurrency=int(os.environ.get("CIV_CONC","10")))
    rows=[]; traj_rows=[]
    def checkpoint():
        if traj_rows:
            with open(os.path.join(OUT,"trajectory.csv"),"w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=list(traj_rows[0].keys())); w.writeheader(); w.writerows(traj_rows)
        if rows:
            with open(os.path.join(OUT,"summary.csv"),"w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    async def cell(cond,f0,seed):
        traj=await run_pop(llm,a.model,cond,f0,seed,a.n,a.gens,a.rounds)
        for g,fr in enumerate(traj): traj_rows.append(dict(model=a.model,cond=cond,f0=f0,seed=seed,gen=g,defector_frac=fr))
        rows.append(dict(model=a.model,cond=cond,f0=f0,seed=seed,d_start=traj[0],d_end=traj[-1],
                         invaded=int(traj[-1]>traj[0]), fixed_D=int(traj[-1]==1.0), fixed_C=int(traj[-1]==0.0)))
        checkpoint()
        print(f"{cond} f0={f0} s{seed}: D {traj[0]:.2f}->{traj[-1]:.2f} traj={traj} calls={llm.calls} cost=${llm.total_cost:.2f}",flush=True)
    await asyncio.gather(*[cell(c,f,s) for c in ["anon","reputation"] for f in F0 for s in seeds])
    checkpoint()
    print("DONE replicator calls",llm.calls,"cost",round(llm.total_cost,3),"fallbacks",llm.fallback_hits)

if __name__=="__main__": asyncio.run(main())
