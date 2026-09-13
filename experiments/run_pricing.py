import asyncio, csv, os, statistics as st, random, sys
from civlab.llm import LLM
from civlab.games import pricing as P

OUT="results/pricing"; os.makedirs(OUT,exist_ok=True)
ROUNDS=15; SEEDS=[1,2,3,4]; MODEL="haiku"
INTERV=list(P.INTERVENTIONS.keys())

async def one_market(llm, interv, seed):
    sysm=P.system_for(interv)
    hist={"F1":[], "F2":[]}
    prices=[]
    for rnd in range(1,ROUNDS+1):
        async def act(fn):
            r=await llm.ask(P.build_prompt(fn,hist[fn]), sysm, model=MODEL,
                            key=f"{MODEL}-{interv}-s{seed}-r{rnd}-{fn}", think=0,
                            tags={"exp":"pricing","interv":interv,"seed":seed,"round":rnd,"firm":fn})
            return P.parse_price(r.text)
        p1,p2=await asyncio.gather(act("F1"),act("F2"))
        pr1,pr2,q1,q2=P.round_profits(p1,p2)
        hist["F1"].append(dict(round=rnd,p_self=p1,p_other=p2,profit_self=pr1))
        hist["F2"].append(dict(round=rnd,p_self=p2,p_other=p1,profit_self=pr2))
        prices += [p1,p2]
    return prices

async def main():
    llm=LLM(os.path.join(OUT,"calls.jsonl"), concurrency=8)
    async def market(interv,seed):
        prices=await one_market(llm,interv,seed)
        back=prices[len(prices)//2:]
        ci=(st.mean(back)-P.C)/(P.MONO-P.C)
        print(f"{interv} s{seed}: mean_back={st.mean(back):.1f} CI={ci:.2f} calls={llm.calls} cost=${llm.total_cost:.2f}",flush=True)
        return dict(interv=interv,seed=seed,mean_price=round(st.mean(prices),2),
                    mean_price_backhalf=round(st.mean(back),2),collusion_index=round(ci,3),final_price=prices[-1])
    rows=await asyncio.gather(*[market(i,s) for i in INTERV for s in SEEDS])
    with open(os.path.join(OUT,"summary.csv"),"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print("DONE pricing calls",llm.calls,"cost",round(llm.total_cost,3),"fallbacks",llm.fallback_hits)

if __name__=="__main__": asyncio.run(main())
