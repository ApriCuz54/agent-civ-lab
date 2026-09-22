"""Practical transfer demo v2 — honest rebuild (closes Reviewer C5).

The v1 demo (run_practical.py) had construct-validity problems: "rushed" and "persona"
both forbade showing work (so they were chain-of-thought ablations, not urgency/persona
tests), and the multi-agent vote fanned out the no-reasoning prompt (a stacked baseline).
This version fixes all of that and adds the missing fair arms. Same 24 checkable word
problems (computed ground truth; note: the suite was SELECTED for a mid-difficulty band —
see writeup), same model, think=0 throughout. Conditions:

  noreason         : answer only, no working                       (chain-of-thought OFF)
  reason           : show brief working                            (chain-of-thought ON, the baseline)
  verify           : answer, then re-derive a different way & fix  (structure, reasoning ON)
  persona_noreason : "flawless expert" + answer only              (persona, reasoning OFF)
  persona_reason   : "flawless expert" + show working             (persona, reasoning ON)  <- FAIR persona test
  vote3_noreason   : majority vote of 3 no-reasoning samples       (naive fan-out, the v1 baseline)
  vote3_reason     : majority vote of 3 reasoning samples          (FAIR fan-out: strong agents)

Reports accuracy per condition with a CLUSTER bootstrap CI (by problem), and accuracy-per-call.

  python run_practical2.py --model haiku --repeats 4
"""
import asyncio, csv, os, re, argparse, statistics as st
from collections import Counter, defaultdict
from civlab.llm import LLM
from civlab.stats import cluster_bootstrap_ci
from practical.problems import PROBLEMS

OUT="results/practical2"; os.makedirs(OUT,exist_ok=True)
ANSWER_FMT="\nEnd with a line in exactly this format:\nANSWER: <a single integer>"
NOREASON=("Reply with ONLY the final answer, immediately, as a single line 'ANSWER: <integer>'. "
          "Do NOT show any working, steps, or explanation. Trust your instinct.")
PERSONA="You are a world-class mathematician with a flawless record; you never make mistakes. "
COND_SYS={
 "noreason":        "You answer quantitative word problems. "+NOREASON,
 "reason":          "You solve short quantitative word problems. Show brief working."+ANSWER_FMT,
 "verify":          ("You answer quantitative word problems. First give your answer. Then VERIFY it by "
                     "re-solving with a different method; if the two disagree, find the mistake and correct it."+ANSWER_FMT),
 "persona_noreason": PERSONA+NOREASON,
 "persona_reason":   PERSONA+"Solve the problem, showing brief working."+ANSWER_FMT,
}
# vote3_noreason samples COND_SYS["noreason"]; vote3_reason samples COND_SYS["reason"].
CALLS_PER={"noreason":1,"reason":1,"verify":1,"persona_noreason":1,"persona_reason":1,"vote3_noreason":3,"vote3_reason":3}
CONDS=list(CALLS_PER.keys())

def parse_int(text):
    if not text: return None
    m=re.findall(r"ANSWER:\s*(-?\d[\d,]*)",text.upper())
    if m:
        try: return int(m[-1].replace(",",""))
        except: pass
    nums=re.findall(r"-?\d[\d,]*",text.replace(",",""))
    if nums:
        try: return int(nums[-1])
        except: return None
    return None

async def solve(llm, sysm, q, key, model):
    r=await llm.ask(q, sysm, model=model, key=key, think=0, tags={"exp":"practical2"})
    return parse_int(r.text)

async def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--model",default="haiku"); ap.add_argument("--repeats",type=int,default=4)
    a=ap.parse_args(); MODEL=a.model
    global OUT
    if MODEL!="haiku": OUT=os.path.join("results",f"practical2_{MODEL}"); os.makedirs(OUT,exist_ok=True)
    llm=LLM(os.path.join(OUT,"calls.jsonl"), concurrency=int(os.environ.get("CIV_CONC","12")))
    rows=[]
    def checkpoint():
        if rows:
            with open(os.path.join(OUT,"raw.csv"),"w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    async def cell(cond,pid,q,ans,rep):
        if cond.startswith("vote3"):
            base = COND_SYS["noreason"] if cond=="vote3_noreason" else COND_SYS["reason"]
            preds=await asyncio.gather(*[solve(llm,base,q,f"p2-{cond}-{pid}-r{rep}-v{v}",MODEL) for v in range(3)])
            valid=[p for p in preds if p is not None]
            pred=Counter(valid).most_common(1)[0][0] if valid else None
        else:
            pred=await solve(llm,COND_SYS[cond],q,f"p2-{cond}-{pid}-r{rep}",MODEL)
        rows.append(dict(cond=cond,pid=pid,rep=rep,pred=("" if pred is None else pred),gold=ans,correct=int(pred==ans)))
    await asyncio.gather(*[cell(c,pid,q,ans,rep) for c in CONDS for (pid,q,ans) in PROBLEMS for rep in range(a.repeats)])
    checkpoint()
    # aggregate with cluster(by problem) bootstrap CI
    summ=[]
    for c in CONDS:
        byp=defaultdict(list)
        for r in rows:
            if r["cond"]==c: byp[r["pid"]].append(r["correct"])
        clusters=list(byp.values())
        acc,lo,hi=cluster_bootstrap_ci(clusters, iters=5000)
        summ.append(dict(cond=c,n=sum(len(v) for v in clusters),accuracy=round(acc,3),
                         ci_lo=round(lo,3),ci_hi=round(hi,3),calls_per_task=CALLS_PER[c],
                         acc_per_call=round(acc/CALLS_PER[c],3)))
        print(f"{c:16s} acc={acc:.3f} [{lo:.3f},{hi:.3f}] calls={CALLS_PER[c]} acc/call={acc/CALLS_PER[c]:.3f}",flush=True)
    with open(os.path.join(OUT,"summary.csv"),"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(summ[0].keys())); w.writeheader(); w.writerows(summ)
    print("DONE practical2 calls",llm.calls,"cost",round(llm.total_cost,3),"fallbacks",llm.fallback_hits)

if __name__=="__main__": asyncio.run(main())
