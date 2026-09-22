import csv, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
rows={r["cond"]:r for r in csv.DictReader(open("results/practical2/summary.csv"))}
order=["noreason","persona_noreason","vote3_noreason","reason","persona_reason","verify","vote3_reason"]
label={"noreason":"answer only\n(no reasoning)","persona_noreason":"“flawless expert”\n+ no reasoning",
       "vote3_noreason":"3 agents vote\n(no reasoning)","reason":"show working\n(reasoning)",
       "persona_reason":"“flawless expert”\n+ reasoning","verify":"reason + verify\n(re-derive & fix)",
       "vote3_reason":"3 agents vote\n(reasoning)"}
BAD="#d1495b"; GOOD="#2f9e6f"
col={"noreason":BAD,"persona_noreason":BAD,"vote3_noreason":BAD,"reason":GOOD,"persona_reason":GOOD,"verify":GOOD,"vote3_reason":GOOD}
acc=[float(rows[c]["accuracy"])*100 for c in order]
lo=[float(rows[c]["ci_lo"])*100 for c in order]; hi=[float(rows[c]["ci_hi"])*100 for c in order]
calls=[int(rows[c]["calls_per_task"]) for c in order]
err=[[a-l for a,l in zip(acc,lo)],[h-a for a,h in zip(acc,hi)]]
fig,ax=plt.subplots(figsize=(12,5.6))
x=range(len(order))
ax.bar(x,acc,color=[col[c] for c in order],yerr=err,capsize=4,error_kw=dict(lw=1.3,ecolor="#333"))
for i,(a,c) in enumerate(zip(acc,calls)):
    ax.text(i,a+1.5,f"{a:.0f}%"+(f"\n{c}×" if c>1 else ""),ha="center",va="bottom",fontsize=9.5,fontweight="bold")
ax.axhline(100,ls=":",c="#999",lw=1)
ax.set_xticks(list(x)); ax.set_xticklabels([label[c] for c in order],fontsize=8.5)
ax.set_ylim(0,112); ax.set_ylabel("Accuracy on 24 word problems (%)")
ax.set_title("The lever is reasoning — not personas, not verification-on-top, not more agents",fontweight="bold")
# divider between reasoning-off and reasoning-on families
ax.axvline(2.5,color="#bbb",lw=1,ls="--")
ax.text(1,107,"reasoning OFF",ha="center",color=BAD,fontsize=10,fontweight="bold")
ax.text(4.75,107,"reasoning ON",ha="center",color=GOOD,fontsize=10,fontweight="bold")
plt.tight_layout(); plt.savefig("results/practical2/practical2_figure.png",dpi=120)
print("wrote results/practical2/practical2_figure.png")
