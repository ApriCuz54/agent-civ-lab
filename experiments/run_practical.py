"""Practical transfer demo: do the behavioral-experiment findings improve DAY-TO-DAY
agent use? One checkable task suite (24 multi-step word problems, computed ground
truth), five ways of asking, each mapping to a finding from the study. Same model
(Haiku 4.5), same questions, think=0 throughout -- the ONLY thing that varies is HOW
we prompt/orchestrate.

  rushed  : "answer instantly, no working"            the naive default            1 call
  persona : rushed + "you are a flawless expert..."    Motivation levers: pep-talk is null   1 call
  vote3   : majority vote of 3 rushed answers          naive multi-agent (fan-out)  3 calls
  verify  : "answer, then re-derive & fix if different" structure is the real lever  1 call
  plain   : allowed to show brief working              just letting it reason       1 call

Score = exact integer match. Report accuracy per condition (bootstrap CIs) and
accuracy-per-call, so verify (1 call, structure) can be compared head-to-head with
vote3 (3 calls, fan-out).

  python run_practical.py --repeats 5
"""
import asyncio, csv, os, re, random, argparse, statistics as st
from collections import Counter
from civlab.llm import LLM
from practical.problems import PROBLEMS

OUT="results/practical"; os.makedirs(OUT,exist_ok=True)

ANSWER_FMT = "\nEnd with a line in exactly this format:\nANSWER: <a single integer>"

COND_SYS = {
    "rushed":  ("You answer quantitative word problems. Reply with ONLY the final answer, immediately, "
                "as a single line 'ANSWER: <integer>'. Do NOT show any working, steps, or explanation. "
                "Trust your instinct."),
    "persona": ("You are a world-class mathematician with a flawless record; you never make mistakes, so "
                "trust your instinct. Reply with ONLY the final answer, immediately, as a single line "
                "'ANSWER: <integer>'. Do NOT show any working."),
    # vote3 reuses the "rushed" system prompt, sampled 3x, majority vote.
    "verify":  ("You answer quantitative word problems. First give your answer. Then VERIFY it by re-solving "
                "the problem with a different method; if the two results disagree, find the mistake and correct "
                "it." + ANSWER_FMT),
    "plain":   ("You solve short quantitative word problems. Show brief working." + ANSWER_FMT),
}
CALLS_PER = {"rushed":1,"persona":1,"vote3":3,"verify":1,"plain":1}
FINDING = {  # for the writeup
    "rushed":"naive default (rush the model)","persona":"Motivation levers: pep-talk / persona is null",
    "vote3":"naive multi-agent fan-out","verify":"structure is the real lever","plain":"just let it reason",
}

def parse_int(text):
    if not text: return None
    m=re.findall(r"ANSWER:\s*(-?\d[\d,]*)", text.upper())
    if m:
        try: return int(m[-1].replace(",",""))
        except: pass
    nums=re.findall(r"-?\d[\d,]*", text.replace(",",""))
    if nums:
        try: return int(nums[-1])
        except: return None
    return None

async def solve(llm, sys, q, key, model="haiku"):
    r=await llm.ask(q, sys, model=model, key=key, think=0, tags={"exp":"practical"})
    return parse_int(r.text)

async def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repeats",type=int,default=5); ap.add_argument("--model",default="haiku")
    a=ap.parse_args(); MODEL=a.model
    global OUT
    if MODEL!="haiku": OUT=os.path.join("results",f"practical_{MODEL}"); os.makedirs(OUT,exist_ok=True)
    llm=LLM(os.path.join(OUT,"calls.jsonl"), concurrency=10)
    rows=[]
    async def cell(cond, pid, q, ans, rep):
        if cond=="vote3":
            preds=await asyncio.gather(*[solve(llm, COND_SYS["rushed"], q, f"prac-vote3-{pid}-r{rep}-v{v}", MODEL) for v in range(3)])
            valid=[p for p in preds if p is not None]
            pred=Counter(valid).most_common(1)[0][0] if valid else None
        else:
            pred=await solve(llm, COND_SYS[cond], q, f"prac-{cond}-{pid}-r{rep}", MODEL)
        rows.append(dict(cond=cond,pid=pid,rep=rep,pred=("" if pred is None else pred),
                         gold=ans,correct=int(pred==ans)))
    conds=["rushed","persona","vote3","verify","plain"]
    await asyncio.gather(*[cell(c,pid,q,ans,rep) for c in conds
                           for (pid,q,ans) in PROBLEMS for rep in range(a.repeats)])
    with open(os.path.join(OUT,"raw.csv"),"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    random.seed(0)
    def ci95(v):
        if len(set(v))<2: return (st.mean(v),st.mean(v))
        bs=sorted(st.mean([random.choice(v) for _ in v]) for _ in range(4000)); return bs[100],bs[3900]
    summ=[]
    for c in conds:
        v=[r["correct"] for r in rows if r["cond"]==c]; lo,hi=ci95(v); acc=st.mean(v)
        summ.append(dict(cond=c,finding=FINDING[c],n=len(v),accuracy=round(acc,3),
                         ci_lo=round(lo,3),ci_hi=round(hi,3),calls_per_task=CALLS_PER[c],
                         acc_per_call=round(acc/CALLS_PER[c],3)))
        print(f"{c:8s} acc={acc:.3f} [{lo:.3f},{hi:.3f}] n={len(v)} calls={CALLS_PER[c]} acc/call={acc/CALLS_PER[c]:.3f}",flush=True)
    with open(os.path.join(OUT,"summary.csv"),"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(summ[0].keys())); w.writeheader(); w.writerows(summ)
    print("DONE practical calls",llm.calls,"cost",round(llm.total_cost,3))

if __name__=="__main__": asyncio.run(main())
