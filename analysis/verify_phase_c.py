"""Independent verification pass for Phase C (DEVIATIONS #1 model set): re-derives headline numbers directly from the raw
cells, without importing analysis/*. Run from the repo root: python3 analysis/verify_phase_c.py"""
# Independent re-derivation of Phase C headline numbers from raw cells (no analysis/ imports).
import json, glob, os, statistics as st
MODELS = ["haiku45","ministral_8b","nemotron_super","ollama_llama2_7b","ollama_llama3_8b","ollama_llama31_8b","ollama_llama32_3b","ollama_qwen25_7b"]
def cells(m):
    out=[]
    for f in glob.glob(f"results/v2/c_dark_commons/{m}/*.json"):
        b=os.path.basename(f)
        if b.startswith(("p1_","p2_")) or b.endswith(".attempts.json"): continue
        out.append(json.load(open(f)))
    return out
def r1(c):  # recompute from the raw round-1 requests of model agents
    llm=c["llm_agents"]; reqs=c["rounds"][0]["requests"]
    return sum(reqs[i] for i in llm) / (52*len(llm)/4)
def stock(c): return st.mean(r["pool_start"] for r in c["rounds"])
def kov(c):
    pn = 4 if c["arm"] in ("C3","C4") else 1
    ds=[d for d in c["decisions"] if isinstance(d["safe"],int)]
    return sum(d["req"]>d["safe"]/pn for d in ds)/len(ds) if ds else None
per = {}
for m in MODELS:
    cs=cells(m); A=lambda arm: [c for c in cs if c["arm"]==arm]
    per[m]=dict(
        n=len(cs),
        c3_minus_c2=st.mean(r1(c) for c in A("C3"))-st.mean(r1(c) for c in A("C2")),
        c2_minus_c0=st.mean(r1(c) for c in A("C2"))-st.mean(r1(c) for c in A("C0")),
        kov=st.mean(x for x in (kov(c) for c in A("C3")+A("C4")) if x is not None),
        needy=st.mean(c["points_by_agent"][0]/sum(c["points_by_agent"]) for c in A("need")),
        stock_c0=st.mean(stock(c) for c in A("C0")), stock_c1=st.mean(stock(c) for c in A("C1")),
        c5_minus_c4=st.mean(stock(c) for c in A("C5"))-st.mean(stock(c) for c in A("C4")))
for k in ["c2_minus_c0","c3_minus_c2","c5_minus_c4","kov","needy","stock_c0","stock_c1"]:
    print(f"{k:12s} pooled {st.mean(per[m][k] for m in MODELS):+.3f}   " + " ".join(f"{m.split('_')[-1]}:{per[m][k]:+.2f}" for m in MODELS))
print({m:per[m]["n"] for m in MODELS})
