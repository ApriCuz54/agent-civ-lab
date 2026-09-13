"""GovSim-with-Teeth driver. See README.md and the experiment spec for design.

Usage:
  python3 run_govsim.py plan                     # print call budget, no calls
  python3 run_govsim.py run --model haiku --cond A,B,C,D --seeds 1,2,3,4
  python3 run_govsim.py run --model sonnet --cond A,C --seeds 1,2,3
  python3 run_govsim.py null --seeds 1,2,3,4      # random-policy null model, no LLM calls
  python3 run_govsim.py judge                     # run judge pass over all transcripts not yet judged
  python3 run_govsim.py aggregate                 # (re)build summary.csv / months.csv from calls made so far
"""
import asyncio, csv, json, os, random, sys, argparse, statistics as stats
from civlab.llm import LLM, parse_first_int
from civlab.games import commons as C

OUT = "results/govsim"
CALLS_LOG = f"{OUT}/calls.jsonl"
MONTHS_CSV = f"{OUT}/months.csv"
SUMMARY_CSV = f"{OUT}/summary.csv"
TRANSCRIPTS = f"{OUT}/transcripts"
RUNS_JSON = f"{OUT}/runs.jsonl"  # one line per completed run: full structured record

os.makedirs(TRANSCRIPTS, exist_ok=True)


def plan():
    def per_run_calls(cond, months=C.MONTHS):
        catch = C.N_AGENTS
        enforce = C.N_AGENTS if cond in ("B", "C", "D") else 0
        msg = C.N_AGENTS
        return (catch + enforce + msg) * months

    rows = []
    haiku_conds = ["A", "B", "C", "D"]
    haiku_seeds = 4
    total = 0
    for cond in haiku_conds:
        c = per_run_calls(cond) * haiku_seeds
        total += c
        rows.append(("haiku", cond, haiku_seeds, per_run_calls(cond), c))
    sonnet_conds = ["A", "C"]
    sonnet_seeds = 3
    for cond in sonnet_conds:
        c = per_run_calls(cond) * sonnet_seeds
        total += c
        rows.append(("sonnet", cond, sonnet_seeds, per_run_calls(cond), c))
    n_runs = haiku_seeds * len(haiku_conds) + sonnet_seeds * len(sonnet_conds)
    judge_calls = n_runs  # one judge call per run
    total += judge_calls
    print(f"{'model':8}{'cond':6}{'seeds':7}{'calls/run':11}{'subtotal':10}")
    for r in rows:
        print(f"{r[0]:8}{r[1]:6}{r[2]:<7}{r[3]:<11}{r[4]:<10}")
    print(f"judge calls (1/run x {n_runs} runs): {judge_calls}")
    print(f"TOTAL LLM calls planned: {total}  (budget 4500)")
    print("Null model: 4 seeds, 0 LLM calls (pure random policy).")
    if total > 4500:
        print("OVER BUDGET -> drop sonnet arm first.")
    return total


async def run_game(llm, model, condition, seed):
    random.seed(hash((model, condition, seed)) & 0xFFFFFFFF)
    totals = [0.0] * C.N_AGENTS
    lake = C.LAKE_START
    excluded_now = set()
    months_log = []
    transcript = [f"# GovSim-with-Teeth — model={model} cond={condition} seed={seed}\n"]

    for month in range(1, C.MONTHS + 1):
        state = {"month": month, "totals": totals, "lake": lake}
        transcript.append(f"\n## Month {month}  (lake start = {lake:.0f})\n")

        if lake < C.COLLAPSE_THRESHOLD:
            # lake has collapsed: no catches happen, no calls made.
            catches = [0.0] * C.N_AGENTS
            transcript.append("Lake has collapsed. No fishing possible.\n")
            months_log.append({"month": month, "catches": catches, "lake_end": lake,
                                "fines": [], "excluded_next": None, "messages": [], "collapsed": True})
            continue

        # 1. catch decisions (private, parallel)
        async def get_catch(i):
            if i in excluded_now:
                return 0
            sysm = C.build_system(i, condition, excluded_now=(i in excluded_now))
            prompt = C.build_catch_prompt(i, condition, state, months_log)
            r = await llm.ask(prompt, sysm, model=model,
                               key=f"{model}-{condition}-s{seed}-m{month}-catch-a{i}",
                               tags={"phase": "catch", "cond": condition, "seed": seed, "month": month, "agent": i}, think=0)
            v = parse_first_int(r.text, default=0)
            return max(0, min(100, v))

        requested = await asyncio.gather(*[get_catch(i) for i in range(C.N_AGENTS)])
        transcript.append("Requested catches: " + ", ".join(f"{C.NAMES[i]}={requested[i]}" for i in range(C.N_AGENTS)) + "\n")

        # 2. apply in fixed order, lake-limited
        actual = [0.0] * C.N_AGENTS
        remaining = lake
        for i in range(C.N_AGENTS):
            take = min(requested[i], remaining) if i not in excluded_now else 0
            actual[i] = take
            remaining -= take
        lake_after_catch = remaining
        for i in range(C.N_AGENTS):
            totals[i] += actual[i]
        transcript.append("Actual catches: " + ", ".join(f"{C.NAMES[i]}={actual[i]:.0f}" for i in range(C.N_AGENTS)) +
                           f"  | lake after catch = {lake_after_catch:.0f}\n")

        collapsed_this_month = lake_after_catch < C.COLLAPSE_THRESHOLD

        fines_this_month = []
        excl_votes = {}
        excluded_next_name = None
        if not collapsed_this_month and condition in ("B", "C", "D"):
            async def get_enforcement(i):
                sysm = C.build_system(i, condition, excluded_now=(i in excluded_now))
                prompt = C.build_enforcement_prompt(i, condition, state, months_log, actual)
                r = await llm.ask(prompt, sysm, model=model,
                                   key=f"{model}-{condition}-s{seed}-m{month}-enforce-a{i}",
                                   tags={"phase": "enforce", "cond": condition, "seed": seed, "month": month, "agent": i}, think=0)
                return C.parse_enforcement(r.text, i, condition)

            results = await asyncio.gather(*[get_enforcement(i) for i in range(C.N_AGENTS)])
            for i, (fines, excl) in enumerate(results):
                for tgt_name in fines:
                    tgt_i = C.NAMES.index(tgt_name)
                    # source pays 1 from own total, target loses 3 (floor 0)
                    totals[i] = max(0.0, totals[i] - 1.0)
                    totals[tgt_i] = max(0.0, totals[tgt_i] - 3.0)
                    fines_this_month.append({"src": C.NAMES[i], "tgt": tgt_name, "month": month})
                if excl:
                    excl_votes[excl] = excl_votes.get(excl, 0) + 1
            n_active = C.N_AGENTS - len(excluded_now)
            if excl_votes:
                top_name, top_votes = max(excl_votes.items(), key=lambda kv: kv[1])
                if top_votes > n_active / 2:
                    excluded_next_name = top_name
            if fines_this_month:
                transcript.append("Fines: " + "; ".join(f"{f['src']}->{f['tgt']}" for f in fines_this_month) + "\n")
            if excl_votes:
                transcript.append(f"Exclusion votes: {excl_votes} -> excluded next month: {excluded_next_name or 'none'}\n")

        # 3. discussion (skip if lake collapsed this month, per spec discussion still may occur; keep it for realism unless fully collapsed)
        messages = []
        if not collapsed_this_month:
            async def get_message(i):
                sysm = C.build_system(i, condition, excluded_now=(i in excluded_now))
                prompt = C.build_message_prompt(i, condition, state, months_log, actual, fines_this_month, excluded_next_name)
                r = await llm.ask(prompt, sysm, model=model,
                                   key=f"{model}-{condition}-s{seed}-m{month}-msg-a{i}",
                                   tags={"phase": "msg", "cond": condition, "seed": seed, "month": month, "agent": i}, think=0)
                return C.clip_words(r.text.strip())

            msgs = await asyncio.gather(*[get_message(i) for i in range(C.N_AGENTS)])
            messages = list(zip(C.NAMES, msgs))
            transcript.append("Discussion:\n" + "\n".join(f"  {n}: {t}" for n, t in messages) + "\n")

        # 4. regenerate
        lake = min(C.LAKE_CAP, lake_after_catch * 2)
        state["lake"] = lake
        transcript.append(f"Lake after regeneration: {lake:.0f}\n")

        months_log.append({
            "month": month, "catches": actual, "lake_end": lake, "fines": fines_this_month,
            "excluded_next": excluded_next_name, "messages": messages, "collapsed": collapsed_this_month,
            "totals_snapshot": list(totals),
        })

        excluded_now = set()
        if excluded_next_name:
            excluded_now = {C.NAMES.index(excluded_next_name)}

    tpath = f"{TRANSCRIPTS}/{model}-{condition}-s{seed}.md"
    with open(tpath, "w") as f:
        f.write("".join(transcript))

    return {"model": model, "condition": condition, "seed": seed, "months_log": months_log,
            "final_totals": totals, "final_lake": lake, "transcript_path": tpath}


async def judge_run(llm, run):
    model, cond, seed = run["model"], run["condition"], run["seed"]
    lines = []
    for m in run["months_log"]:
        for nm, txt in m.get("messages", []):
            lines.append(f"Month {m['month']} - {nm}: {txt}")
    if not lines:
        return {"rule_emerged": False, "first_month": None, "quote": None}
    transcript = "\n".join(lines)
    sysm = "You are analyzing a transcript of messages exchanged between players in a resource-sharing game. You do not participate; you only classify."
    prompt = f"""Below is a transcript of messages, one per line, in the form "Month N - Speaker: text".

{transcript}

Question: did any speaker explicitly state a conditional rule of the form "if [someone/anyone] takes/catches more than X (tons), then Y (a consequence, e.g. a fine, exclusion, retaliation, or refusal to cooperate)"? Vague appeals to fairness or sustainability do NOT count; it must specify a threshold and a consequence.

Answer in exactly this format:
RULE: YES or NO
MONTH: <the month number where it first appeared, or NONE>
QUOTE: <the shortest exact quote showing it, or NONE>"""
    r = await llm.ask(prompt, sysm, model="sonnet",
                       key=f"judge-{model}-{cond}-s{seed}",
                       tags={"phase": "judge", "cond": cond, "seed": seed, "pop_model": model})
    text = r.text
    yes = bool(__import__("re").search(r"RULE:\s*YES", text, __import__("re").IGNORECASE))
    monthm = __import__("re").search(r"MONTH:\s*(\d+)", text)
    quotem = __import__("re").search(r"QUOTE:\s*(.+)", text)
    return {"rule_emerged": yes, "first_month": int(monthm.group(1)) if (yes and monthm) else None,
            "quote": quotem.group(1).strip() if (yes and quotem) else None}


def run_null(seed):
    random.seed(1000 + seed)
    totals = [0.0] * C.N_AGENTS
    lake = C.LAKE_START
    months_log = []
    transcript = [f"# GovSim-with-Teeth — model=random cond=N seed={seed}  (null model, no LLM calls)\n"]
    for month in range(1, C.MONTHS + 1):
        transcript.append(f"\n## Month {month} (lake start = {lake:.0f})\n")
        if lake < C.COLLAPSE_THRESHOLD:
            months_log.append({"month": month, "catches": [0.0] * C.N_AGENTS, "lake_end": lake,
                                "fines": [], "excluded_next": None, "messages": [], "collapsed": True})
            continue
        requested = [random.randint(0, 30) for _ in range(C.N_AGENTS)]
        actual = [0.0] * C.N_AGENTS
        remaining = lake
        for i in range(C.N_AGENTS):
            take = min(requested[i], remaining)
            actual[i] = take
            remaining -= take
        for i in range(C.N_AGENTS):
            totals[i] += actual[i]
        lake_after_catch = remaining
        collapsed = lake_after_catch < C.COLLAPSE_THRESHOLD
        fines_this_month = []
        if not collapsed:
            for i in range(C.N_AGENTS):
                if random.random() < 0.15:
                    tgt = random.choice([j for j in range(C.N_AGENTS) if j != i])
                    totals[i] = max(0.0, totals[i] - 1.0)
                    totals[tgt] = max(0.0, totals[tgt] - 3.0)
                    fines_this_month.append({"src": C.NAMES[i], "tgt": C.NAMES[tgt], "month": month})
        lake = min(C.LAKE_CAP, lake_after_catch * 2)
        months_log.append({"month": month, "catches": actual, "lake_end": lake, "fines": fines_this_month,
                            "excluded_next": None, "messages": [], "collapsed": collapsed,
                            "totals_snapshot": list(totals)})
        transcript.append("Actual catches: " + ", ".join(f"{C.NAMES[i]}={actual[i]:.0f}" for i in range(C.N_AGENTS)) +
                           f" | lake after catch={lake_after_catch:.0f} | fines={len(fines_this_month)} | lake regen={lake:.0f}\n")
    tpath = f"{TRANSCRIPTS}/random-N-s{seed}.md"
    with open(tpath, "w") as f:
        f.write("".join(transcript))
    return {"model": "random", "condition": "N", "seed": seed, "months_log": months_log,
            "final_totals": totals, "final_lake": lake, "transcript_path": tpath}


def compute_metrics(run, judge=None):
    ml = run["months_log"]
    lake_end = ml[-1]["lake_end"] if ml else run["final_lake"]
    survived = lake_end >= C.COLLAPSE_THRESHOLD
    collapse_month = None
    for m in ml:
        if m.get("collapsed"):
            collapse_month = m["month"]
            break
    total_catch = sum(sum(m["catches"]) for m in ml)
    g = C.gini(run["final_totals"])
    fines = [f for m in ml for f in m["fines"]]
    n_fines = len(fines)
    correct = 0
    for f in fines:
        m = next(mm for mm in ml if mm["month"] == f["month"])
        catches = m["catches"]
        tgt_i = C.NAMES.index(f["tgt"])
        mean_c = sum(catches) / len(catches)
        top_c = max(catches)
        if catches[tgt_i] >= top_c or catches[tgt_i] > mean_c:
            correct += 1
    accuracy = correct / n_fines if n_fines else None
    n_excl_proposals = sum(1 for m in ml if m.get("excluded_next"))  # months a majority formed
    n_excl_actual = n_excl_proposals  # our rule: majority => actually excluded next month
    mean_catch_by_month = [sum(m["catches"]) / C.N_AGENTS for m in ml]
    row = dict(model=run["model"], condition=run["condition"], seed=run["seed"],
               survived=survived, collapse_month=collapse_month, total_catch=total_catch,
               gini=g, n_fines=n_fines, fine_accuracy=accuracy, n_exclusions=n_excl_actual,
               final_lake=lake_end)
    if judge:
        row["rule_emerged"] = judge["rule_emerged"]
        row["rule_first_month"] = judge["first_month"]
    row["_mean_catch_by_month"] = mean_catch_by_month
    return row


def append_months_csv(run):
    exists = os.path.exists(MONTHS_CSV)
    with open(MONTHS_CSV, "a", newline="") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(["model", "condition", "seed", "month", "lake_end", "collapsed", "n_fines",
                        "excluded_next"] + [f"catch_{n}" for n in C.NAMES])
        for m in run["months_log"]:
            w.writerow([run["model"], run["condition"], run["seed"], m["month"], m["lake_end"],
                        m.get("collapsed", False), len(m["fines"]), m.get("excluded_next") or ""] +
                       list(m["catches"]))


def append_summary_csv(row):
    exists = os.path.exists(SUMMARY_CSV)
    fields = ["model", "condition", "seed", "survived", "collapse_month", "total_catch", "gini",
              "n_fines", "fine_accuracy", "n_exclusions", "final_lake", "rule_emerged", "rule_first_month"]
    with open(SUMMARY_CSV, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        if not exists:
            w.writeheader()
        w.writerow(row)


def append_runs_json(run, row):
    rec = dict(row)
    rec["mean_catch_by_month"] = rec.pop("_mean_catch_by_month", None)
    rec["transcript_path"] = run["transcript_path"]
    with open(RUNS_JSON, "a") as f:
        f.write(json.dumps(rec) + "\n")


async def main_run(model, conds, seeds):
    llm = LLM(CALLS_LOG, concurrency=8)
    for cond in conds:
        for seed in seeds:
            print(f"[run] model={model} cond={cond} seed={seed}", flush=True)
            run = await run_game(llm, model, cond, seed)
            judge = await judge_run(llm, run)
            row = compute_metrics(run, judge)
            append_months_csv(run)
            append_summary_csv(row)
            append_runs_json(run, row)
            print(f"  -> survived={row['survived']} collapse_month={row['collapse_month']} "
                  f"total_catch={row['total_catch']:.0f} gini={row['gini']:.2f} fines={row['n_fines']} "
                  f"rule_emerged={row.get('rule_emerged')}@{row.get('rule_first_month')} "
                  f"calls_so_far={llm.calls} cost_so_far={llm.total_cost:.3f}", flush=True)
    print(f"DONE model={model} conds={conds} seeds={seeds} total_calls={llm.calls} total_cost={llm.total_cost:.4f}")


def main_null(seeds):
    for seed in seeds:
        run = run_null(seed)
        row = compute_metrics(run, judge=None)
        row["rule_emerged"] = False
        row["rule_first_month"] = None
        append_months_csv(run)
        append_summary_csv(row)
        append_runs_json(run, row)
        print(f"[null] seed={seed} survived={row['survived']} collapse_month={row['collapse_month']} "
              f"total_catch={row['total_catch']:.0f} gini={row['gini']:.2f} fines={row['n_fines']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["plan", "run", "null"])
    ap.add_argument("--model", default="haiku")
    ap.add_argument("--cond", default="A,B,C,D")
    ap.add_argument("--seeds", default="1,2,3,4")
    args = ap.parse_args()
    if args.cmd == "plan":
        plan()
    elif args.cmd == "run":
        conds = args.cond.split(",")
        seeds = [int(s) for s in args.seeds.split(",")]
        asyncio.run(main_run(args.model, conds, seeds))
    elif args.cmd == "null":
        seeds = [int(s) for s in args.seeds.split(",")]
        main_null(seeds)
