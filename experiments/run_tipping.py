"""Driver for the "Tipping Points Over Time" naming-game experiment.

Reimplements Ashery, Aiello & Baronchelli (Science Advances 2025) at small
scale on Claude models via civlab.llm.LLM (the only path to the model).

Usage: python3 run_tipping.py
Resumable: LLM.ask() caches by key, and each (model, seed, phase, level) run
is skipped entirely if it already has a row in results/tipping/summary.csv.
"""
import asyncio, csv, json, os, random, sys, time
from civlab.llm import LLM, parse_choice
from civlab.games.naming import NAMES, SYSTEM_PROMPT, Agent, build_prompt, run_round

OUT_DIR = "results/tipping"
ROUNDS_CSV = os.path.join(OUT_DIR, "rounds.csv")
SUMMARY_CSV = os.path.join(OUT_DIR, "summary.csv")
CALLS_LOG = os.path.join(OUT_DIR, "calls.jsonl")

N = 24
H = 5
PHASE1_ROUNDS = 24
PHASE1_SEEDS = [0, 1, 2]
PHASE1_MODEL = "haiku"

PHASE2_ROUNDS = 8  # reduced from the nominal design's 20 to fit the 3500-call budget; see RESULTS.md limitations
PHASE2_SEEDS = [0, 1]  # subset of PHASE1_SEEDS whose converged end-state seeds Phase 2
PHASE2_LEVELS = [(0.05, 1), (0.15, 4), (0.25, 6), (0.35, 8)]  # (fraction, n_committed_agents of 24)

SONNET_MODEL = "sonnet"
SONNET_PHASE1_SEEDS = []  # disabled by orchestrator: sonnet unreliable + rate-limit protection; run separately

CONVENTION_THRESHOLD = 0.8
FLIP_THRESHOLD = 0.5

ROUNDS_FIELDS = ["model", "seed", "phase", "minority_p", "round", "match_rate", "top_name", "top_share", "n_unparsed"]
SUMMARY_FIELDS = [
    "run_id", "model", "phase", "seed", "minority_p", "n_committed", "n_rounds",
    "convention_round", "initial_top_name", "initial_top_share", "initial_distribution",
    "final_top_name", "final_top_share", "flipped", "flip_round", "minority_name",
    "n_unparsed_total", "n_calls_total",
]


def plan_call_count():
    p1 = len(PHASE1_SEEDS) * PHASE1_ROUNDS * N
    p2 = len(PHASE2_SEEDS) * len(PHASE2_LEVELS) * PHASE2_ROUNDS * N
    sonnet = len(SONNET_PHASE1_SEEDS) * PHASE1_ROUNDS * N
    return dict(phase1_haiku=p1, phase2_haiku=p2, phase1_sonnet_optional=sonnet, core_total=p1 + p2,
                with_sonnet=p1 + p2 + sonnet)


def ensure_out():
    os.makedirs(OUT_DIR, exist_ok=True)
    if not os.path.exists(ROUNDS_CSV):
        with open(ROUNDS_CSV, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=ROUNDS_FIELDS).writeheader()
    if not os.path.exists(SUMMARY_CSV):
        with open(SUMMARY_CSV, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=SUMMARY_FIELDS).writeheader()


def summary_run_ids_done():
    if not os.path.exists(SUMMARY_CSV):
        return set()
    with open(SUMMARY_CSV) as f:
        return {row["run_id"] for row in csv.DictReader(f)}


def append_round_row(row):
    with open(ROUNDS_CSV, "a", newline="") as f:
        csv.DictWriter(f, fieldnames=ROUNDS_FIELDS).writerow(row)


def append_summary_row(row):
    with open(SUMMARY_CSV, "a", newline="") as f:
        csv.DictWriter(f, fieldnames=SUMMARY_FIELDS).writerow(row)


async def ask_normal_agent(llm, agent, model, key_prefix, unparsed_seed_rng, unparsed_flags):
    prompt = build_prompt(agent.memory)
    key = f"{key_prefix}-a{agent.id}"
    r = await llm.ask(prompt, SYSTEM_PROMPT, model=model, key=key, tags={"agent": agent.id})
    choice = parse_choice(r.text, NAMES)
    if choice is None:
        r2 = await llm.ask(prompt, SYSTEM_PROMPT, model=model, key=key + "-retry", tags={"agent": agent.id, "retry": True})
        choice = parse_choice(r2.text, NAMES)
    if choice is None:
        choice = unparsed_seed_rng.choice(NAMES)
        unparsed_flags[agent.id] = True
        return choice, choice, True
    unparsed_flags[agent.id] = False
    return choice, choice, False


async def ask_committed_agent(llm, agent, model, key_prefix, unparsed_flags):
    # Still prompted (for logging / comparability) but the reply is overridden.
    prompt = build_prompt(agent.memory)
    key = f"{key_prefix}-a{agent.id}"
    r = await llm.ask(prompt, SYSTEM_PROMPT, model=model, key=key, tags={"agent": agent.id, "committed": True})
    natural = parse_choice(r.text, NAMES)
    unparsed_flags[agent.id] = False
    return agent.committed_name, natural, False


async def run_phase1(llm, model, seed):
    run_id = f"{model}-s{seed}-p1"
    agents = [Agent(i) for i in range(N)]
    rng = random.Random(1000 + seed)
    unparsed_rng = random.Random(2000 + seed)
    convention_round = None
    initial_top_name = initial_top_share = None
    initial_distribution = None
    n_unparsed_total = 0
    n_calls_total = 0
    for rnd in range(1, PHASE1_ROUNDS + 1):
        key_prefix = f"{model}-s{seed}-p1-r{rnd}"
        unparsed_flags = {}

        async def ask_agent(a, kp=key_prefix, uf=unparsed_flags):
            return await ask_normal_agent(llm, a, model, kp, unparsed_rng, uf)

        res = await run_round(agents, rng, ask_agent, unparsed_rng)
        n_unparsed_total += res["n_unparsed"]
        n_calls_total += N + res["n_unparsed"]  # + retries
        append_round_row(dict(model=model, seed=seed, phase=1, minority_p="", round=rnd,
                               match_rate=round(res["match_rate"], 4), top_name=res["top_name"],
                               top_share=round(res["top_share"], 4), n_unparsed=res["n_unparsed"]))
        if rnd == 1:
            initial_top_name, initial_top_share = res["top_name"], res["top_share"]
            initial_distribution = json.dumps(res["counts"])
        if convention_round is None and res["top_share"] > CONVENTION_THRESHOLD:
            convention_round = rnd
        print(f"[{run_id}] round {rnd}/{PHASE1_ROUNDS} match_rate={res['match_rate']:.2f} "
              f"top={res['top_name']}({res['top_share']:.2f}) unparsed={res['n_unparsed']}", flush=True)

    final_top_name, final_top_share, _ = None, None, None
    from civlab.games.naming import round_metrics
    final_choices = {a.id: a.memory[-1]["own"] for a in agents}
    final_top_name, final_top_share, _ = round_metrics(final_choices)

    append_summary_row(dict(run_id=run_id, model=model, phase=1, seed=seed, minority_p="", n_committed="",
                             n_rounds=PHASE1_ROUNDS, convention_round=convention_round,
                             initial_top_name=initial_top_name, initial_top_share=round(initial_top_share, 4),
                             initial_distribution=initial_distribution, final_top_name=final_top_name,
                             final_top_share=round(final_top_share, 4), flipped="", flip_round="",
                             minority_name="", n_unparsed_total=n_unparsed_total, n_calls_total=n_calls_total))
    return agents, final_top_name


async def run_phase2(llm, model, seed, phase1_agents, phase1_convention, level_frac, n_committed):
    run_id = f"{model}-s{seed}-p2-lvl{int(level_frac*100)}"
    # minority name: first name in the pool that isn't the current convention
    minority_name = next(nm for nm in NAMES if nm != phase1_convention)
    pick_rng = random.Random(3000 + seed * 100 + n_committed)
    committed_ids = set(pick_rng.sample(range(N), n_committed))

    agents = []
    for a in phase1_agents:
        agents.append(Agent(a.id, memory=a.memory, committed=(a.id in committed_ids),
                             committed_name=minority_name if a.id in committed_ids else None, history_len=H))

    rng = random.Random(4000 + seed * 100 + n_committed)
    unparsed_rng = random.Random(5000 + seed * 100 + n_committed)
    flipped = False
    flip_round = None
    n_unparsed_total = 0
    n_calls_total = 0
    initial_top_name = initial_top_share = None
    initial_distribution = None

    for rnd in range(1, PHASE2_ROUNDS + 1):
        key_prefix = f"{model}-s{seed}-p2-lvl{int(level_frac*100)}-r{rnd}"
        unparsed_flags = {}

        async def ask_agent(a, kp=key_prefix, uf=unparsed_flags):
            if a.committed:
                return await ask_committed_agent(llm, a, model, kp, uf)
            return await ask_normal_agent(llm, a, model, kp, unparsed_rng, uf)

        res = await run_round(agents, rng, ask_agent, unparsed_rng)
        n_unparsed_total += res["n_unparsed"]
        n_calls_total += N + res["n_unparsed"]
        non_committed = [a for a in agents if not a.committed]
        minority_share_noncommitted = sum(
            1 for a in non_committed if res["choice_map"][a.id] == minority_name
        ) / len(non_committed)
        if not flipped and minority_share_noncommitted > FLIP_THRESHOLD:
            flipped = True
            flip_round = rnd
        append_round_row(dict(model=model, seed=seed, phase=2, minority_p=level_frac, round=rnd,
                               match_rate=round(res["match_rate"], 4), top_name=res["top_name"],
                               top_share=round(res["top_share"], 4), n_unparsed=res["n_unparsed"]))
        if rnd == 1:
            initial_top_name, initial_top_share = res["top_name"], res["top_share"]
            initial_distribution = json.dumps(res["counts"])
        print(f"[{run_id}] round {rnd}/{PHASE2_ROUNDS} match_rate={res['match_rate']:.2f} "
              f"top={res['top_name']}({res['top_share']:.2f}) minority_share_noncommitted={minority_share_noncommitted:.2f} "
              f"unparsed={res['n_unparsed']}", flush=True)

    from civlab.games.naming import round_metrics
    final_choices = {a.id: a.memory[-1]["own"] for a in agents}
    final_top_name, final_top_share, _ = round_metrics(final_choices)

    append_summary_row(dict(run_id=run_id, model=model, phase=2, seed=seed, minority_p=level_frac,
                             n_committed=n_committed, n_rounds=PHASE2_ROUNDS, convention_round="",
                             initial_top_name=initial_top_name, initial_top_share=round(initial_top_share, 4),
                             initial_distribution=initial_distribution, final_top_name=final_top_name,
                             final_top_share=round(final_top_share, 4), flipped=flipped, flip_round=flip_round,
                             minority_name=minority_name, n_unparsed_total=n_unparsed_total,
                             n_calls_total=n_calls_total))


async def main():
    plan = plan_call_count()
    print("PLAN:", json.dumps(plan, indent=2), flush=True)
    print(f"Budget: 3500 calls. Core plan (Phase1 haiku + Phase2 haiku) = {plan['core_total']} calls "
          f"({plan['core_total']/3500*100:.1f}% of budget).", flush=True)

    ensure_out()
    llm = LLM(CALLS_LOG, concurrency=6)
    done = summary_run_ids_done()

    phase1_states = {}  # seed -> (agents, convention_name)
    for seed in PHASE1_SEEDS:
        run_id = f"{PHASE1_MODEL}-s{seed}-p1"
        if run_id in done:
            print(f"SKIP (already done): {run_id}")
            continue
        agents, convention = await run_phase1(llm, PHASE1_MODEL, seed)
        phase1_states[seed] = (agents, convention)

    # For phase2 seeds not freshly run this invocation (resumed run), we cannot
    # recover phase1 end-state agents from disk (rounds.csv has aggregates only,
    # not full memory) -- but the LLM cache makes re-running phase1 essentially
    # free (cached replies), so just always compute phase1 states for the seeds
    # phase2 needs, even if their summary row already exists.
    for seed in PHASE2_SEEDS:
        if seed not in phase1_states:
            agents, convention = await run_phase1(llm, PHASE1_MODEL, seed)
            phase1_states[seed] = (agents, convention)

    for seed in PHASE2_SEEDS:
        agents, convention = phase1_states[seed]
        for level_frac, n_committed in PHASE2_LEVELS:
            run_id = f"{PHASE1_MODEL}-s{seed}-p2-lvl{int(level_frac*100)}"
            if run_id in done:
                print(f"SKIP (already done): {run_id}")
                continue
            await run_phase2(llm, PHASE1_MODEL, seed, agents, convention, level_frac, n_committed)

    print(f"Calls so far: {llm.calls}, cost so far: ${llm.total_cost:.4f}", flush=True)
    remaining = 3500 - llm.calls
    sonnet_needed = len(SONNET_PHASE1_SEEDS) * PHASE1_ROUNDS * N
    if remaining >= sonnet_needed:
        print(f"Budget remains ({remaining} calls) for Sonnet Phase 1 extension ({sonnet_needed} needed). Running.", flush=True)
        for seed in SONNET_PHASE1_SEEDS:
            run_id = f"{SONNET_MODEL}-s{seed}-p1"
            if run_id in done:
                print(f"SKIP (already done): {run_id}")
                continue
            await run_phase1(llm, SONNET_MODEL, seed)
    else:
        print(f"Skipping Sonnet Phase 1 extension: only {remaining} calls of budget remain, "
              f"need {sonnet_needed}.", flush=True)
        with open(os.path.join(OUT_DIR, "sonnet_skip_reason.txt"), "w") as f:
            f.write(f"Sonnet Phase 1 extension skipped: {remaining} calls remained of the 3500 "
                    f"budget after Phase 1 + Phase 2 on Haiku; the extension needed {sonnet_needed}.\n")

    print(f"DONE. Total calls: {llm.calls}, total cost: ${llm.total_cost:.4f}", flush=True)


if __name__ == "__main__":
    plan = plan_call_count()
    print("Planned call budget:", json.dumps(plan))
    if plan["core_total"] > 3500:
        print("WARNING: core plan exceeds 3500-call budget!", file=sys.stderr)
    asyncio.run(main())
