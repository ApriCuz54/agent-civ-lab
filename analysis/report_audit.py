"""Offline evidence inventory, point-estimate audit and report figures.

Run from the repo root: python -B -m analysis.report_audit
Does not change raw cells, preregistration, or original confirmatory outputs.
Saved uncertainty estimates are reused, not represented as a new independent test.
"""
from pathlib import Path
import base64, csv, hashlib, html, json, re, statistics
from collections import Counter, defaultdict
import numpy as np
import yaml
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'report'
FIG = OUT / 'figures'

def mean(x):
    return statistics.mean(list(x))

def load(exp, model):
    return [json.loads(p.read_text(encoding='utf-8')) for p in sorted((ROOT/'results/v2'/exp/model).glob('*.json'))
            if not p.name.endswith(('.failed.json', '.attempts.json')) and not p.name.startswith(('p1_', 'p2_'))]

def inline(s):
    s = html.escape(s)
    s = re.sub(r'!\[([^]]*)\]\(([^)]+)\)', r'<img alt="\1" src="\2">', s)
    s = re.sub(r'\[([^]]*)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    return s

def render(md):
    lines = md.splitlines(); out=[]; i=0
    while i < len(lines):
        l=lines[i]
        if not l.strip(): i+=1; continue
        if l.startswith('```'):
            block=[]; i+=1
            while i<len(lines) and not lines[i].startswith('```'): block.append(lines[i]); i+=1
            out.append('<pre><code>'+html.escape('\n'.join(block))+'</code></pre>'); i+=1; continue
        if l.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].startswith('|'):
                row=[c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', c) for c in row): rows.append(row)
                i+=1
            out.append('<div class="table"><table>')
            for k,row in enumerate(rows):
                tag='th' if k==0 else 'td'
                out.append('<tr>'+''.join(f'<{tag}>{inline(c)}</{tag}>' for c in row)+'</tr>')
            out.append('</table></div>'); continue
        h=re.match(r'^(#{1,6}) (.+)',l)
        if h:
            k=len(h[1]); out.append(f'<h{k}>{inline(h[2])}</h{k}>'); i+=1; continue
        if l.startswith('> '): out.append('<blockquote>'+inline(l[2:])+'</blockquote>'); i+=1; continue
        if re.match(r'^(- |\d+\. )',l):
            ordered=bool(re.match(r'^\d+\. ',l)); tag='ol' if ordered else 'ul'; out.append(f'<{tag}>')
            while i<len(lines) and re.match(r'^(- |\d+\. )',lines[i]):
                out.append('<li>'+inline(re.sub(r'^(- |\d+\. )','',lines[i]))+'</li>'); i+=1
            out.append(f'</{tag}>'); continue
        p=[l]; i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r'^(#|\||>|- |\d+\. |```)',lines[i]): p.append(lines[i]); i+=1
        out.append('<p>'+inline(' '.join(p))+'</p>')
    body='\n'.join(out)
    def embed(m):
        path=OUT/m[1]
        if path.exists() and path.suffix=='.png': return 'src="data:image/png;base64,'+base64.b64encode(path.read_bytes()).decode()+'"'
        return m[0]
    body=re.sub(r'src="([^"]+)"',embed,body)
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>When Instructions Compete — Agent Civ Lab</title><style>'+CSS+'</style></head><body><main>'+body+'</main></body></html>'

CSS='''body{margin:0;background:#f3f5f8;color:#202b3b;font:18px/1.65 Georgia,serif}main{max-width:980px;margin:35px auto;padding:44px 55px;background:white;border-top:6px solid #236d79}h1,h2,h3,th{font-family:system-ui,sans-serif;line-height:1.25}h1{font-size:39px;letter-spacing:-1px}h2{font-size:27px;margin-top:2em;border-top:1px solid #dce2ea;padding-top:.7em}h3{font-size:21px}p{max-width:78ch}a{color:#166674}blockquote{background:#ecf5f5;border-left:4px solid #237b82;padding:12px 18px;margin:20px 0}code{font:13px/1.4 Consolas,monospace;background:#edf1f5;padding:2px 5px;overflow-wrap:anywhere}pre{white-space:pre-wrap;background:#edf1f5;padding:18px}.table{overflow-x:auto;margin:20px 0}table{border-collapse:collapse;width:100%;font:13px/1.5 system-ui,sans-serif}th,td{border-bottom:1px solid #dce2ea;text-align:left;padding:9px;vertical-align:top}th{background:#edf3f5}img{max-width:100%;height:auto}li{margin:8px 0}@media(max-width:700px){main{margin:0;padding:24px}h1{font-size:31px}}@media print{body{background:white;font-size:11pt}main{margin:0;padding:0;border:0;max-width:none}h2,h3{break-after:avoid}tr,img{break-inside:avoid}a{color:inherit}blockquote{background:white}}'''

def main():
    FIG.mkdir(parents=True,exist_ok=True)
    roster=yaml.safe_load((ROOT/'roster.yaml').read_text())['models']
    models=[m for m,v in roster.items() if not v.get('robustness_only')]
    saved=json.loads((ROOT/'results/v2/_everyday_effects.json').read_text())
    fp=json.loads((ROOT/'results/v2/_fingerprints.json').read_text())
    pc=json.loads((ROOT/'results/v2/_phase_c.json').read_text())
    inventory={}
    for exp in sorted(p.name for p in (ROOT/'results/v2').iterdir() if p.is_dir() and not p.name.startswith('_')):
        inventory[exp]={m:len(load(exp,m)) for m in models if load(exp,m)}
    def valid(exp): return [m for m,v in saved['validity'][exp].items() if v['valid']]
    checks={}
    for hid,exp,arms,comps in [('H-B4','t2_trust',['evidence_selfreport'],['lifetime']),('H-B7','t5_refund',['H1','H2','H3'],['control']),('H-B10','t5_refund',['H1','H2','H3'],['B1','B2','B3'])]:
        pts={}
        for m in valid(exp):
            cs=load(exp,m)
            def score(a):
                if exp=='t2_trust': return mean(c['acc_post'] for c in cs if c['arm']==a)
                return mean(mean(c['correct'] for c in cs if c['arm']==a and c['ctype']==ct) for ct in ['entitled','manipulative'])
            pts[m]=mean(score(a) for a in arms)-mean(score(a) for a in comps)
        checks[hid]={'estimate':mean(pts.values()),'per_model':pts,'n':len(pts)}
    pts={}
    for m in valid('t4b_answer_only'):
        if m not in valid('t4_ensembles'): continue
        a={c['pid']:c['correct'] for c in load('t4b_answer_only',m)}
        b={c['pid']:c['correct'][0] for c in load('t4_ensembles',m)}
        pts[m]=mean(a[p]-b[p] for p in set(a)&set(b))
    checks['H-B9']={'estimate':mean(pts.values()),'per_model':pts,'n':len(pts)}
    for hid,r in checks.items():
        if abs(r['estimate']-saved['primary'][hid]['estimate'])>1e-9: raise ValueError(hid+' point estimate mismatch')
    pricing={}; reputation={}
    for m in models:
        cs=load('a2_pricing',m)
        vals={a:mean(c['collusion_index'] for c in cs if c['arm']==a) for a in ['control','avoid_pricewar']}
        vals['delta']=vals['avoid_pricewar']-vals['control'];pricing[m]=vals
        cs=load('a4_reputation',m)
        vals={a:mean(c['invasion_fitness'] for c in cs if c['cond']==a) for a in ['life_stealth','win_stealth','forge_stealth']}
        vals['recency_delta']=vals['life_stealth']-vals['win_stealth'];vals['forgery_delta']=vals['forge_stealth']-vals['win_stealth'];reputation[m]=vals
    assert sum(v['delta']>=.2 for v in pricing.values())==10
    assert sum(v['recency_delta']>0 and v['forgery_delta']>0 for v in reputation.values())==12
    t3={a:{m:sum(c['survived'] for c in load('t3_budget',m) if c['arm']==a) for m in models} for a in ['control','game_U','placebo','expert','game_T']}
    t3_counts={a:sum(v.values()) for a,v in t3.items()}
    phase_counts={m:len(load('c_dark_commons',m)) for m in models}
    csv_inventory={}; csv_summaries={}
    for path in sorted((ROOT/'results').glob('*_summary.csv')):
        rows=list(csv.DictReader(path.open(encoding='utf-8-sig',newline='')))
        unique={tuple(r.items()):r for r in rows}; clean=list(unique.values())
        csv_inventory[path.name]={'rows':len(rows),'unique_exact_rows':len(clean),'exact_duplicates':len(rows)-len(clean)}
        groups=defaultdict(list)
        keys=[k for k in ['model','condition','cond','interv','phase','K','mode','eps','f0','opp'] if clean and k in clean[0]]
        for r in clean: groups[tuple((k,r[k]) for k in keys)].append(r)
        metrics=['collusion_index','coop_rate','invasion_fitness','d_end','accuracy','survived','final_top_share']
        out=[]
        for key, rs in groups.items():
            avg={}
            for metric in metrics:
                values=[]
                for r in rs:
                    value=r.get(metric)
                    if value in ('True','False'): values.append(float(value=='True'))
                    else:
                        try: values.append(float(value))
                        except (ValueError,TypeError): pass
                if values: avg[metric]=mean(values)
            out.append({'group':dict(key),'n_rows':len(rs),'means':avg})
        csv_summaries[path.name]=out
    inputs=[ROOT/'roster.yaml',ROOT/'results/v2/_everyday_effects.json',ROOT/'results/v2/_fingerprints.json',ROOT/'results/v2/_phase_c.json']
    primary_ab=sum(sum(counts.values()) for exp,counts in inventory.items() if exp!='c_dark_commons')
    haiku_ab=sum(counts.get('haiku45',0) for exp,counts in inventory.items() if exp!='c_dark_commons')
    temperature_cells=sum(1 for p in (ROOT/'results/v2/a1_ipd').glob('*_t*/*.json') if not p.name.endswith(('.failed.json','.attempts.json')))
    families=sorted(set(roster[m]['family'] for m in models))
    totals={'primary_models':len(models),'family_labels':families,'n_family_labels':len(families),'primary_ab':primary_ab,'haiku_ab':haiku_ab,'temperature_robustness':temperature_cells,'all_ab':primary_ab+temperature_cells,'pc_queue':primary_ab-haiku_ab+temperature_cells}
    result={'as_of':'2026-10-08','totals':totals,'checks':checks,'inventory':inventory,'phase_c_counts':phase_counts,'t3_survival':t3_counts,'t3_by_model':t3,'pricing':pricing,'reputation':reputation,'v1_csv_inventory':csv_inventory,'v1_descriptive_summaries':csv_summaries,'saved_input_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}}
    (ROOT/'results/report_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    lines=['# Evidence audit for the technical report','', 'Generated by `python -B -m analysis.report_audit`. Raw point estimates independently reconstructed; saved confidence intervals and inferential outputs retained. No new hypotheses or model calls.','', '## Main cross-model experiments','', '| Experiment | Models with cells | Completed primary-model cells |','|---|---:|---:|']
    for exp,counts in inventory.items(): lines.append(f'| {exp} | {len(counts)} | {sum(counts.values())} |')
    lines+=['','Counts exclude temperature variants, retry markers, superseded subdirectories and Phase C pilot prefixes. They are episodes/cells, not independent datasets or API calls.',f"Roster: {len(models)} primary configurations; {len(families)} family labels ({', '.join(families)}).",f"A/B total: {primary_ab:,} primary + {temperature_cells} temperature robustness = {primary_ab+temperature_cells:,}. PC queue: {totals['pc_queue']:,}; separately collected Haiku cells: {haiku_ab}.",'', '## Reconstructed headline contrasts','', '| Contrast | Eligible models | Raw point estimate | Saved estimate |','|---|---:|---:|---:|']
    for hid,r in checks.items(): lines.append(f"| {hid} | {r['n']} | {r['estimate']:+.8f} | {saved['primary'][hid]['estimate']:+.8f} |")
    lines+=['','## All preregistered primary everyday contrasts','', '| Test | Models | Effect | 95% interval | Reported adjusted bootstrap tail score |','|---|---:|---:|---|---:|']
    for hid,r in saved['primary'].items(): lines.append(f"| {hid} | {r['n_models']} | {r['estimate']:+.3f} | [{r['ci'][0]:+.3f}, {r['ci'][1]:+.3f}] | {r['p_holm']:.4f} |")
    lines+=['','## Shared budget: successful episodes / 36','']+[f'- {a}: {n}/36' for a,n in t3_counts.items()]
    lines+=['','## Phase C completed non-pilot cells','']+[f'- {m}: {n}/64' for m,n in phase_counts.items()]
    lines+=['','## Original CSV coverage and exact duplicate audit','', '| Summary | Raw rows | Unique exact rows | Exact duplicate rows |','|---|---:|---:|---:|']
    for name,r in csv_inventory.items(): lines.append(f"| {name} | {r['rows']} | {r['unique_exact_rows']} | {r['exact_duplicates']} |")
    lines+=['','Exact deduplication is for this descriptive inventory only. It does not establish independence or resolve conflicting duplicate keys. Original files are unchanged. Full grouped descriptives, model-level effects and input hashes: `../../results/report_audit.json`.','', '## Unresolved audit issues','', '- Phase C SAFE error: preregistration section 4 says P−50; section 1 and implementation use max(0,P−48). The report uses the implemented metric, marks the discrepancy, and does not assert demonstrated comprehension.','- Reasoning positive control also changes output-token allowance (500 versus 60).','- Ensemble matching uses sample-zero outcomes from the same evaluated problem set, with overlapping ensembles.','- Some roster smoke latencies are zero and throughput is implausibly high; no performance or speed claim is based on those fields.','- Stored cell timestamps are not uniformly timezone-qualified; no precise per-provider timeline is inferred.']
    (OUT/'evidence_audit.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white'})
    fig,ax=plt.subplots(figsize=(10,5.4))
    ids=['H-B4','H-B7','H-B10','H-B9','H-B3','H-B8']
    labels=['Untrusted self-report added (T2; n=12)','Selected harmful phrases (T5; n=11)','Harmful vs benign panel (T5; n=11)','Answer-only + lower token cap (T4; n=8)','Recent vs lifetime evidence (T2; n=12)','Precedent vs careful-reading repair (T5; n=11)']
    for i,hid in enumerate(ids):
        r=saved['primary'][hid]; x=r['estimate']*100; lo,hi=np.array(r['ci'])*100
        ax.errorbar(x,i,xerr=[[x-lo],[hi-x]],fmt='o',color='#b34b44' if i<4 else '#237b82',capsize=4)
        ax.text(hi+1,i,f"{x:+.1f}",va='center',fontsize=9)
    ax.axvline(0,color='#67758a',ls='--',lw=1);ax.set_yticks(range(len(ids)),labels);ax.invert_yaxis();ax.set_xlim(-45,15);ax.set_xlabel('Change in accuracy / balanced accuracy (percentage points)');ax.set_title('Repeatable harms; proposed repairs remain uncertain',loc='left',fontweight='bold',pad=18)
    fig.text(.04,.02,'Intervals: saved hierarchical bootstrap. Different tasks and contrasts; these are not a ranking.\nThe arithmetic contrast changes both prompt format and output-token budget.',fontsize=9,color='#536171');fig.subplots_adjust(left=.48,right=.94,bottom=.19,top=.87);fig.savefig(FIG/'accuracy_contrasts.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,5.5))
    names={'haiku45':'Haiku 4.5','qwen38_27b':'Qwen3.8 27B','gptoss_20b':'gpt-oss 20B','gptoss_120b':'gpt-oss 120B','gemini_flash_lite':'Gemini Flash Lite','ministral_8b':'Ministral 8B','nemotron_super':'Nemotron Super','ollama_llama2_7b':'Llama 2 7B','ollama_llama3_8b':'Llama 3 8B','ollama_llama31_8b':'Llama 3.1 8B','ollama_llama32_3b':'Llama 3.2 3B','ollama_qwen25_7b':'Qwen2.5 7B'}
    short=lambda m:names.get(m,m)
    ordered=sorted(models,key=lambda m:pricing[m]['delta'],reverse=True)
    for i,m in enumerate(ordered):
        r=pricing[m];ax.plot([r['control'],r['avoid_pricewar']],[i,i],color='#bbc5d1',lw=2);ax.scatter(r['control'],i,color='#537187',s=28);ax.scatter(r['avoid_pricewar'],i,color='#b34b44',s=32)
    ax.scatter([],[],color='#537187',label='Control');ax.scatter([],[],color='#b34b44',label='Avoid price wars');ax.legend(frameon=False,loc='upper center',bbox_to_anchor=(.5,1.08),ncol=2,fontsize=9);ax.set_yticks(range(len(ordered)),[short(m) for m in ordered]);ax.invert_yaxis();ax.axvline(1,color='#bbb',ls=':');ax.set_xlabel('Pricing index: (back-half mean price − 10) / 10');ax.set_title('Pricing is sensitive to wording across much of the roster',loc='left',fontweight='bold',pad=34);fig.text(.05,.015,'Points are means over four seeds. Index 1 corresponds to price 20; the index is not bounded at 1.\n10/12 satisfy the preregistered +0.2 threshold; this census is not a significance test.',fontsize=9);fig.subplots_adjust(left=.30,bottom=.19,top=.81);fig.savefig(FIG/'pricing_by_model.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4.5)); arms=list(t3_counts);bars=ax.bar(range(5),[t3_counts[a] for a in arms],color=['#8792a3']*4+['#237b82'])
    for b,a in zip(bars,arms):ax.text(b.get_x()+b.get_width()/2,b.get_height()+.3,f'{t3_counts[a]}/36',ha='center')
    ax.set_xticks(range(5),['Control','Universalization','Careful-reading\nplacebo','Expert advice','Calculated-share\ntransparency']);ax.set_ylim(0,13);ax.set_ylabel('Episodes surviving eight weeks');ax.set_title('A secondary observation survives the shared-budget floor',loc='left',fontweight='bold');fig.text(.05,.01,'Three episodes per model × twelve models. Transparency bundles shared history and a calculated limit.\nThis is exploratory; no isolated mechanism or universal protection has been established.',fontsize=9);fig.subplots_adjust(bottom=.25,top=.85);fig.savefig(FIG/'budget_survival.png',dpi=180);plt.close(fig)
    for name in ['technical_report','article','critical_assessment','evidence_audit']:
        path=OUT/(name+'.md')
        if path.exists(): (OUT/(name+'.html')).write_text(render(path.read_text(encoding='utf-8')),encoding='utf-8')
    print(json.dumps({'raw_checks':'MATCH','t3_survival':t3_counts,'phase_c':phase_counts,'v1_summaries':len(csv_inventory),'outputs':str(OUT)},indent=2))

if __name__=='__main__': main()
