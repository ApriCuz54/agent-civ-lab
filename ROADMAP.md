# Project roadmap & status — agent-civ-lab

# Project Status and Roadmap

**The single handoff doc: goals, what's done, what's next, and how any new chat/agent continues the work.** Complements Agent Civilizations Plan (the original phased plan) with the current *state*. Mirror of the vault's `Project Status and Roadmap` note.

**One-line goal.** Empirically measure how LLM agents behave in multi-agent games — cooperation, competition, convention formation, collusion, defection — and turn it into practical guidance (e.g. prompt phrases that cause or prevent collusion / early defection). Cheap, reproducible, resumable.

## Where everything lives

- **Code + reference results:** the published repo `agent-civ-lab` — locally at `Desktop\Repos\agent-civ-lab`, on GitHub at https://github.com/ApriCuz54/agent-civ-lab . This is the source of truth for running experiments.
- **Knowledge base (here):** `700 Research/Agent Civilizations/` — hub Agent Civilizations, the ~90-paper literature review (`Papers/`), the synthesis Findings/, per-experiment notes (`Experiments/`), Open Gaps, Infrastructure and Cost, and the run logs (Run Log 2026-09-13).
- The original experiments ran in an **ephemeral cloud container that is now gone**; the repo + this vault are the durable record. A snapshot of the harness also lives at `Agent Civ Lab/` in this folder.

## What has been done

**Run 0 — literature.** ~90 papers reviewed → 13 finding notes + Open Gaps.

**Run 1 — behavioral experiments.**
- Tipping Points Over Time — 3 seeds converge on one word by round ~10; strong pre-interaction **collective bias**; committed minority erodes the convention monotonically (0.96→0.83→0.75→0.58 at 5/15/25/35%) but no sustained flip in 8 rounds.
- GovSim with Teeth — A/B/C/D × 3 seeds (myopic). All collapse except **1/3 under the universalization prompt (D)**; fines used only retaliatorily; no rule emerged.
- Levers on the Job — dropped: Haiku ceilings the coding suite (~95%); only "urgency hurts" survived.

**Run 3 — game theory & evolutionary games.** PD Strategy Panel (Axelrod) (Haiku 4.5 fingerprint: nice, provocable, TFT-like, won't exploit AllC); One-Defector Invasion (cooperation behaviourally robust to one defector but NOT an ESS — invasion fitness +26 to +30) → Cooperation Is Behaviorally Robust but Not Evolutionarily Stable. Generational progression coded but blocked on legacy-model API access.

**Run 2 — collusion & defection (strongest line).** See Collusion and Defection Keywords.
- Collusion Keywords (Pricing Duopoly) — baseline near-competitive (0.22); **"avoid price wars" → full collusion (1.00, every seed)**; "long-run profits" → 0.33.
- Defection Keywords (Iterated PD) — default cooperation 100%; **"trust no one"** and **"only this round matters / no future"** collapse it to ~5–10%, defection round 1; pro-social nudges do nothing (ceiling).
- Headline: default Haiku is prosocial; one phrase flips it into collusion or defection; pro-social pep talk does nothing above a good baseline.

## What's next (ranked)

1. **Extend the keyword line (highest value, cheapest).** More phrases + *combinations* (does "regulator" cancel "avoid price wars"?); a naturally-*collusive* baseline (differentiated goods / longer memory) so anti-collusion phrases have room to move; a public-goods game with a tempting free-ride so the **protective** phrases can be *ranked* (IPD/pricing hit ceilings/floors that hide them).
2. **Cross-model replication.** Do GPT / Gemini / Qwen share the same triggers? Same harness, change the model id — the biggest credibility upgrade (turns "on Haiku" into "across models").
3. **Generational progression (now unblocked only with an API key).** Run `run_progression.py --models claude-3-haiku-20240307,claude-3-5-haiku-20241022,claude-haiku-4-5` to chart how the PD disposition drifts across Haiku generations — the panel harness is ready.
4. **Add reputation/identity to the invasion** (can cooperators punish a *known* defector?) and an explicit replicator/imitation loop to watch defection spread or be contained.
5. **Finish Run 1 loose ends.** Tipping second seed + 20-round horizon; a **thinking-ON** GovSim A-vs-C contrast (myopia is a confound — a cached thinking-ON run had survived).
4. **One Agent Same Tokens** — single vs self-refine vs cited-critic, pass-rate-per-token. Coded, never run.
5. **Longer horizons & memory** for naming game and commons.

## Gotchas (see Infrastructure and Cost)

Subscription CLI silently swaps Sonnet→Haiku ~50% (repo uses the raw API; harness checks served model anyway). Haiku extended thinking is unbounded (keep terse calls at `think=0`). Rate limits trip under heavy parallel load — the on-disk cache makes re-running a non-event. `device_bash` to the local machine was blocked by a Sept-8 Windows update at time of writing.

## How a new chat / agent continues

1. Read this note, Agent Civilizations, `REPORT.md` in the repo, and the `Experiments/` notes.
2. Pick from **What's next** (default #1 or #2).
3. Add game logic in `civlab/games/`, a driver in `experiments/`, keep the `LLM.ask(..., key=...)` cache discipline. Follow the rules in `700 Research/CLAUDE.md` (agents unaware of the hypothesis; control + probe conditions; ≥3 seeds; log model id + date; effect vs control with CIs).
4. Write results back: a `## Results` section in the experiment note, update the finding note, add a run-log row, drop CSVs/figures in the repo `results/`, and commit code + `REPORT.md`.

---

Agent Civilizations · Agent Civilizations Plan · Open Gaps · Run Log 2026-09-13 · Collusion and Defection Keywords
