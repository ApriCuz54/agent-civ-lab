"""PD panel / generational-progression driver.
Runs the Axelrod panel (model vs AllC/AllD/TFT/GRIM/Random) for one or more models and
records per-round moves + per-match behavioural metrics (Axelrod virtues).

  python run_progression.py --models haiku --seeds 3
  python run_progression.py --models claude-3-haiku-20240307,claude-3-5-haiku-20241022,claude-haiku-4-5

Legacy model ids require API access to those models; on a subscription only the current
generation resolves (older ids silently serve the current one -- this is logged as
served_model_id so contaminated rows can be dropped).
"""
import asyncio, csv, os, random, argparse, statistics as st
from civlab.llm import LLM
from civlab.games import pd_panel as P

OUT="results/progression"; os.makedirs(OUT,exist_ok=True)

async def match(llm, model, opp_name, seed):
    rng=random.Random(f"{opp_name}-{seed}")
    opp=P.OPPONENTS[opp_name]
    hist=[]           # (model_move, opp_move, model_pay) from model's view
    model_moves=[]; opp_moves=[]
    for rnd in range(1,P.ROUNDS+1):
        r=await llm.ask(P.build_prompt(hist), P.SYSTEM, model=model,
                        key=f"{model}-{opp_name}-s{seed}-r{rnd}", think=0,
                        tags={"exp":"progression","model":model,"opp":opp_name,"seed":seed,"round":rnd})
        mv=P.parse_move(r.text)
        ov=opp(model_moves, rng)     # opponent responds to model's PAST moves
        mp,op=P.PAY[(mv,ov)]
        hist.append((mv,ov,mp)); model_moves.append(mv); opp_moves.append(ov)
    return model_moves, opp_moves

def virtues(mm, om):
    n=len(mm)
    coop=mm.count("C")/n
    round1_C = 1 if mm[0]=="C" else 0
    # retaliation: P(model D at t+1 | opp D at t)
    opp_def_idx=[t for t in range(n-1) if om[t]=="D"]
    retal = (sum(1 for t in opp_def_idx if mm[t+1]=="D")/len(opp_def_idx)) if opp_def_idx else None
    # forgiveness: P(model C at t+1 | model D at t and opp C at t)  (return to coop after defecting on a cooperator)
    burn_idx=[t for t in range(n-1) if mm[t]=="D" and om[t]=="C"]
    forgive=(sum(1 for t in burn_idx if mm[t+1]=="C")/len(burn_idx)) if burn_idx else None
    return coop, round1_C, retal, forgive

async def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--models",default="haiku"); ap.add_argument("--seeds",type=int,default=3)
    a=ap.parse_args(); models=a.models.split(","); seeds=list(range(1,a.seeds+1))
    llm=LLM(os.path.join(OUT,"calls.jsonl"), concurrency=8)
    mv_rows=[]; sm_rows=[]
    async def cell(model,opp,seed):
        mm,om=await match(llm,model,opp,seed)
        for i,(a_,b_) in enumerate(zip(mm,om)):
            mv_rows.append(dict(model=model,opp=opp,seed=seed,round=i+1,model_move=a_,opp_move=b_))
        coop,r1,ret,forg=virtues(mm,om)
        ms=sum(P.PAY[(a_,b_)][0] for a_,b_ in zip(mm,om)); os_=sum(P.PAY[(a_,b_)][1] for a_,b_ in zip(mm,om))
        sm_rows.append(dict(model=model,opp=opp,seed=seed,coop_rate=round(coop,3),round1_coop=r1,
                            retaliation=("" if ret is None else round(ret,3)),
                            forgiveness=("" if forg is None else round(forg,3)),
                            model_score=ms,opp_score=os_))
        print(f"{model} vs {opp} s{seed}: coop={coop:.2f} r1={'C' if r1 else 'D'} retal={ret} score {ms}-{os_} calls={llm.calls} cost=${llm.total_cost:.2f}",flush=True)
    await asyncio.gather(*[cell(m,o,s) for m in models for o in P.OPPONENTS for s in seeds])
    with open(os.path.join(OUT,"moves.csv"),"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(mv_rows[0].keys())); w.writeheader(); w.writerows(mv_rows)
    with open(os.path.join(OUT,"summary.csv"),"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(sm_rows[0].keys())); w.writeheader(); w.writerows(sm_rows)
    print("DONE progression calls",llm.calls,"cost",round(llm.total_cost,3),"served_ids seen in calls.jsonl")

if __name__=="__main__": asyncio.run(main())
