---
type: note
project: "[[Agent Civilizations]]"
updated: 2026-09-17
status: In progress
tags:
  - research
  - research/runlog
---
# Cross-Model Run Log — Sonnet extension (started 2026-09-17)

> **Purpose.** The resumable execution record for [[Rigor and Cross-Model Plan]] Phase 1 (running the experiments on Sonnet as well as Haiku). If a session drops, the NEXT session reads THIS note top-to-bottom and continues from the first arm not marked ✅. Everything is cache-resumable — re-running a driver re-does only the missing calls.

## Environment / how to resume

- **Harness:** `agent-civ-lab/` (this session's cloud container). If the container is gone, the code of record is the GitHub repo `ApriCuz54/agent-civ-lab` + local `Desktop\Repos\agent-civ-lab`; re-clone, then re-run. The **cache lives only in the container** (`results/<exp>[_sonnet]/calls.cache.jsonl`) — a fresh container re-runs Sonnet arms from scratch (cost below applies again).
- **Model layer:** `civlab/llm.py` strict guard. `model="sonnet"` is served as `claude-sonnet-4-6` (verified 2026-09-17). Silent Sonnet→Haiku fallback runs ~1 per successful call; the guard retries and never caches a wrong-model reply, so Sonnet data is clean but **effective cost ≈ 2× the raw token cost**.
- **Drivers take `--model sonnet`** (added 2026-09-17 to run_ipd, run_pricing, run_practical; run_invasion/reputation/stealth/progression already had it). Sonnet output goes to `results/<exp>_sonnet/` so Haiku references are untouched. Cache key = sha256(family + system + prompt + key), so Haiku and Sonnet never collide.
- **Resume command per arm is in its row below.** `think=0` throughout (matches Haiku baseline).

### Rate-limit / stop protocol
Session rate limits show as an `api_error` with ~0s duration on every fresh call. When that happens: the cache keeps all completed calls, so just **note the arm as ⏸ PARTIAL with the last-seen call count**, stop, and the next session re-runs the same command to finish it for free. Never delete a `*_sonnet/` dir on a limit — that throws away paid progress.

> [!warning] Sonnet is RATIONED on this subscription — key finding 2026-09-17
> Sonnet (`claude-sonnet-4-6`) is available only as a **trickle**, and the silent Sonnet→Haiku fallback rate **climbs the more Sonnet you use in a window**. Measured this session: first call clean Sonnet (1.9s, 0 fallbacks); by the third call the strict guard could not get Sonnet at all within 4 retries (5 fallbacks, returned Haiku). Sustained throughput fell to **~1 successful Sonnet call/minute, then effectively stalled.** Each fallback is a real Haiku call that still spends quota. **Implication:** Sonnet volume cannot be pushed in a single interactive session; it must be run in **small batches at the start of a fresh usage window** (e.g. ≤~50 calls), stopping the moment the fallback rate spikes. Do NOT lower `strict` to "get through" — that silently contaminates the arm with Haiku (exactly the bug the guard exists to prevent).
>
> **Container caveat:** the cache (`results/<exp>_sonnet/calls.cache.jsonl`) lives ONLY in this cloud container, which is ephemeral. A future session in a NEW container starts with an empty cache and re-runs from scratch. To make progress survive, the cache files must be committed to the repo (see below) and restored before re-running.

## Priority order & status

Legend: ✅ done · ⏸ partial (resume) · ▶ running · ⬜ pending · ❌ failed

| # | Experiment | Sonnet cmd | Haiku ref | Status | Sonnet calls | Sonnet cost | Notes |
|---|---|---|---|---|---|---|---|
| 1 | Defection keywords (IPD) | `CIV_CONC=24 python3 run_ipd.py --model sonnet --seeds 3` | results/ipd/summary.csv | ⏸ | ~8 | ~$0.01 | Started 2026-09-17; **blocked by Sonnet rationing** at ~8 calls. Driver now checkpoints summary per cell + reads CIV_CONC. Resume: same cmd (reuses cache). |
| 2 | PD strategy panel (Axelrod) | `python3 run_progression.py --models sonnet` | results/progression/summary.csv | ⬜ | – | – | 5 opp × 3 seeds × 15 rnd |
| 3 | One-defector invasion | `python3 run_invasion.py --model sonnet` | results/invasion/summary.csv | ⬜ | – | – | 8 agents × 12 rnd × (2 cond) × 4 seeds |
| 4 | Reputation invasion | `python3 run_reputation.py --model sonnet` | results/reputation/summary.csv | ⬜ | – | – | as above |
| 5 | Stealth defector | `python3 run_stealth.py --model sonnet` | results/stealth/summary.csv | ⬜ | – | – | K∈{3,6,9} × 4 seeds |
| 6 | Practical demo | `python3 run_practical.py --model sonnet` | results/practical/summary.csv | ⬜ | – | – | 5 cond × 24 prob × 5 rep |
| 7 | Collusion keywords (pricing) | `python3 run_pricing.py --model sonnet` | results/pricing/summary.csv | ⬜ | – | – | 9 interv × 4 seeds × 15 rnd × 2 |
| – | Tipping / naming (24 agents) | — | results/tipping/ | ⬜ deferred | – | – | too dear on Sonnet (~$100+) |

**Cumulative Sonnet spend this campaign:** $0.00 (updating as we go).

## Per-arm detail & findings
_(Filled in as each arm completes: paired Haiku|Sonnet numbers + the one-line capability-trend read.)_

_None complete yet — see Session 1 below._

## Session log

### Session 1 — 2026-09-17 (infrastructure + throttle discovery)
**Done:**
- Verified `model="sonnet"` is served as `claude-sonnet-4-6` under the strict guard (no contamination).
- Parameterized `run_ipd.py`, `run_pricing.py`, `run_practical.py` with `--model` (others already had it); Sonnet output → `results/<exp>_sonnet/`; cache namespaced by model family (no Haiku/Sonnet collision).
- Added `CIV_CONC` env for concurrency and **per-cell summary checkpointing** to `run_ipd.py` so partial runs are usable/resumable.
- Discovered and documented the **Sonnet rationing / rising-fallback throttle** (see warning box above) — the binding constraint on this whole campaign.

**Blocked:** IPD arm stalled at ~8 Sonnet calls due to rationing. No arm produced results.

**Next session (fresh usage window) — do exactly this:**
1. If in a new container: re-clone the repo, then restore any committed `results/*_sonnet/calls.cache.jsonl` into place before running.
2. Start with the **cheapest single arm** and a **small budget**: `CIV_CONC=16 python3 run_ipd.py --model sonnet --seeds 2`. Watch `fallbacks` in the printed line; **stop when fallbacks climb fast** (throttle hit) — the per-cell checkpoint means whatever finished is saved.
3. When an arm's `summary.csv` exists, add a paired Haiku|Sonnet row to the table above and one trend sentence here.
4. Proceed down the priority list only as the window allows. Consider a **scheduled task at a low-traffic hour** to catch a fresh Sonnet allowance, but remember: a scheduled task = new container = empty cache unless restored.

**Cheapest-first call budgets (for picking what fits a window):** PD panel 1 seed ≈ 75 calls · IPD 2 seeds ≈ 480 · practical 2 reps (rushed/verify/plain only) ≈ 144 · invasion 2 seeds ≈ 340.

