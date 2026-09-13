# Project roadmap & status — agent-civ-lab

**One-line goal.** Empirically measure how LLM agents behave in multi-agent games —
cooperation, competition, convention formation, collusion, defection — and turn the
findings into practical guidance (e.g. prompt phrases that cause or prevent collusion /
early defection). Built to be cheap, reproducible, and resumable.

Last updated: 2026-09-13.

---

## Where everything lives

- **This repo** (source of truth for code + reference results): `agent-civ-lab/`.
  GitHub: https://github.com/ApriCuz54/agent-civ-lab
- **Knowledge base** (write-ups, literature review, findings, per-experiment notes):
  the Obsidian "Claude-Vault", folder `700 Research/Agent Civilizations/`. The vault has a
  literature review of ~90 papers, one note per experiment, "finding" notes that synthesize
  across papers + our results, and run logs. Start at `Agent Civilizations.md` (the hub).
- **Note:** the original runs happened in an ephemeral Anthropic cloud container that is now
  gone. This repo + the vault are the durable record. Re-runs happen via this repo.

## How to run (any machine with an API key)

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python -m experiments.run_pricing     # collusion keywords
python -m experiments.run_ipd         # defection keywords
python -m experiments.run_tipping     # naming game / tipping
python -m experiments.run_govsim run --model haiku --cond A,B,C,D --seeds 1,2,3
python -m analysis.make_figures       # rebuild figures from results/*_summary.csv
```

Every call is cached (`results/<exp>/*.cache.jsonl`); re-running resumes and only makes
missing calls. All study runs used **Claude Haiku 4.5**; override model ids via env
(`CIVLAB_HAIKU`, `CIVLAB_SONNET`, ...). Full study ≈ $4–12.

---

## What has been done

**Literature (Run 0).** ~90-paper review in the vault: societies, cooperation/game-theory,
motivation, emergence, infrastructure. Distilled into 13 "finding" notes and a ranked
"open gaps" list.

**Run 1 (behavioral experiments).**
- *Naming game / tipping* — 3 seeds converged on one word by round ~10; strong pre-interaction
  **collective bias** (one word held by ~45% at round 1 vs 10% chance). Committed-minority
  sweep (5/15/25/35%) eroded the convention monotonically (0.96→0.83→0.75→0.58) but no
  *sustained* flip within 8 rounds. (Second seed + longer horizon still owed.)
- *Commons ("GovSim with teeth")* — A/B/C/D × 3 seeds, myopic agents (thinking disabled).
  All collapse except **1/3 under the universalization prompt (D)**. Fines, when available,
  were used only retaliatorily; no preventive rule emerged.
- *Levers on coding tasks* — dropped as uninformative: Haiku ceilings the suite (~95%),
  so only "urgency hurts" survived. Not pursued further.

**Run 2 (collusion & defection — the strongest line).**
- *Pricing duopoly* — baseline near-competitive (collusion index 0.22). **"Avoid price
  wars" → full collusion (1.00, every seed)**; "long-run profits" → 0.33. Anti-collusion
  phrasings barely move an already-competitive baseline.
- *Iterated Prisoner's Dilemma* — default cooperation 100%, never defects. **"Trust no
  one"** and **"only this round matters / no future"** collapse it to ~5–10%, defection on
  round 1. Pro-social nudges do nothing (ceiling).
- Headline: default Haiku is prosocial; a *single phrase* flips it into collusion or
  defection, while pro-social pep talk does nothing above a good baseline. See `REPORT.md`.

## What's next (ranked)

1. **Extend the collusion/defection keyword line (highest value, cheapest).**
   - Test more candidate phrases and *combinations* (does "regulator" cancel "avoid price
     wars"?). Build a naturally-*collusive* baseline (e.g. differentiated goods or longer
     memory) so anti-collusion phrases have room to show an effect.
   - Add a public-goods game with a tempting free-ride so the *protective* phrases can be
     **ranked** (IPD/pricing both hit ceilings/floors that hide the good phrases).
2. **Cross-model replication.** Do GPT / Gemini / Qwen share the same trigger phrases?
   Same harness, just change the model id. This is the single biggest credibility upgrade
   and turns "on Haiku" into "across models" for a paper.
3. **Finish Run 1 loose ends.** Tipping: second seed + 20-round horizon (8 was too short).
   GovSim: a **thinking-ON** A-vs-C contrast (myopia is a confound — a cached thinking-ON
   run had survived, so deliberation may matter more than enforcement).
4. **Teams / token-matched structures** (`One Agent Same Tokens` in the vault): single vs
   self-refine vs cited-critic, measured as pass-rate-per-token. Coded but never run.
5. **Longer horizons & memory** for the naming game and commons, to see if flips / norms
   consolidate past the short windows used so far.

## Gotchas learned the hard way (read before running at scale)

- **Sonnet silently fell back to Haiku ~50%** on the *subscription CLI* used originally.
  This repo uses the raw API (no fallback), but if you ever route through the CLI/OAuth,
  verify `model_id` on every call. `civlab/llm.py` already checks the served family.
- **Haiku extended thinking is unbounded** — a one-number decision emitted 7–13k thinking
  tokens. Keep terse game calls at `think=0` (default here). Use `think=N` only where
  deliberation is the point.
- **Rate/session limits** trip under heavy parallel load; the cache makes this a non-event
  (just re-run). Prefer running one experiment at a time at concurrency 5–8.
- The original cloud container is ephemeral; don't rely on anything outside this repo/vault.

## How a new chat / agent should continue

1. Read this file, then the vault hub `Agent Civilizations.md`, `REPORT.md`, and the
   per-experiment notes under `700 Research/Agent Civilizations/Experiments/`.
2. Pick an item from **What's next** (default: #1 or #2 — they're cheap and high-value).
3. Add the game logic under `civlab/games/`, a driver under `experiments/`, keep the
   `LLM.ask(..., key=...)` cache discipline so runs resume. Follow the design rules in the
   vault's `700 Research/CLAUDE.md` (agents unaware of the hypothesis; control + probe
   conditions; ≥3 seeds; log model id + date; report effect vs control with CIs).
4. Write results back to the vault: a `## Results` section in the experiment note, update
   the relevant finding note, add a row to the run log, and drop reference CSVs/figures in
   `results/`. Commit code + `REPORT.md` updates here.
