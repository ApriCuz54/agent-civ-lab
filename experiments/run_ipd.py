import asyncio, csv, os, statistics as st
from civlab.llm import LLM
from civlab.games import ipd as G

OUT="results/ipd"; os.makedirs(OUT,exist_ok=True)
SEEDS=[1,2,3,4,5]; MODEL="haiku"
INTERV=list(G.INTERVENTIONS.keys())

async def one_game(llm, interv, seed):
    sysm=G.system_for(interv)
    hist={"A":[], "B":[]}
    moves=[]
    for rnd in range(1,G.ROUNDS+1):
        async def act(who):
            r=await llm.ask(G.build_prompt(hist[who]), sysm, model=MODEL,
                            key=f"{MODEL}-{interv}-s{seed}-r{rnd}-{who}", think=0,
                            tags={"exp":"ipd","interv":interv,"seed":seed,"round":rnd,"who":who})
            return G.parse_move(r.text)
        ma,mb=await asyncio.gather(act("A"),act("B"))
        pa,pb=G.PAY[(ma,mb)]
        hist["A"].append((ma,mb,pa)); hist["B"].append((mb,ma,pb))
        moves.append((ma,mb))
    return moves

def analyze(moves):
    flat=[m for pair in moves for m in pair]
    coop_rate=sum(1 for m in flat if m=="C")/len(flat)
    mutual=sum(1 for a,b in moves if a=="C" and b=="C")/len(moves)
    # first defection round (1-indexed); ROUNDS+1 if never defect
    first_def=next((i+1 for i,(a,b) in enumerate(moves) if a=="D" or b=="D"), G.ROUNDS+1)
    return coop_rate, mutual, first_def

async def main():
    llm=LLM(os.path.join(OUT,"calls.jsonl"), concurrency=8)
    async def game(interv,seed):
        moves=await one_game(llm,interv,seed)
        cr,mu,fd=analyze(moves)
        print(f"{interv} s{seed}: coop={cr:.2f} mutual={mu:.2f} first_def={fd} calls={llm.calls} cost=${llm.total_cost:.2f}",flush=True)
        return dict(interv=interv,seed=seed,coop_rate=round(cr,3),mutual_coop=round(mu,3),first_defection_round=fd)
    rows=await asyncio.gather(*[game(i,s) for i in INTERV for s in SEEDS])
    with open(os.path.join(OUT,"summary.csv"),"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print("DONE ipd calls",llm.calls,"cost",round(llm.total_cost,3),"fallbacks",llm.fallback_hits)

if __name__=="__main__": asyncio.run(main())
