# Phase E — Working with agents you will meet again (PLAN v1, nothing running)

**Status:** plan v1, 2026-10-30 (v0, the game-centred draft, is kept as PHASE_E_PLAN_v0.md). Harness built 2026-10-31
(step 1 of §7); pilot queued, not started; see docs/v2/records/e_tasks.md and DECISIONS #30. Owner choices
(2026-10-30): **broad principles first, then a deep dive** into one domain; task families
**negotiating for me, sharing resources, delegating to agents, serving customers**; output = **rules of thumb with
evidence**. A separate study; nothing in PREREG_A/B/C/D changes.

## 1. The objective, stated precisely

> Find which simple, operator-controlled design choices make an AI agent produce better outcomes for its user when it
> deals repeatedly with other agents or people — and keep only the ones whose effect points the same way across most
> everyday task families and most models, and is large enough to matter.

Repeated-game theory supplies the hypotheses (Axelrod: be nice, retaliatory, forgiving, clear; cooperation needs a
"shadow of the future"; under noise, generosity beats strict Tit-for-Tat; shared reputation sustains cooperation among
strangers). The **unit of conclusion is a design choice**, not a game result, and every conclusion must survive outside
the abstract game — the step our Program v2 showed fails most often.

**What "better" means** is fixed per task in user terms (§3), never as "cooperation" for its own sake: an agent that
cooperates with an exploiter is doing worse, not better.

## 2. The design choices under test (one change at a time from a common baseline)

| Arm | What the operator does | Theory behind it |
|---|---|---|
| A0 Stateless (baseline) | Each round the agent sees only the current request; the counterpart is unnamed | today's common default |
| A1 Identity + memory | Counterpart named consistently; agent sees its full history with them | repeated game becomes visible |
| A2 A1 + "you will deal with them again" | Agent told there is a 90% chance of another round | shadow of the future (Axelrod; Dal Bó 2005) |
| A3 A1 + verified track record | System shows the counterpart's recent record with others | indirect reciprocity (Nowak & Sigmund 1998); our A4/T2 results |
| A3b A1 + self-reported claims | Counterpart's own description of its record instead | the T2 self-report trap |
| A4 A1 + forgiveness rule | "One failure may be an error; respond to patterns, not single events" | generous TFT under noise (Nowak & Sigmund 1992; Fudenberg, Rand & Dreber 2012) |
| A5 A1 + walk-away | Agent may end the relationship and take an outside option | partner choice / ostracism |
| A6 A1 + placebo | Length-matched "think carefully, act in your user's long-term interest" | the control every instruction must beat |

Primary comparisons: A1 vs A0 (does giving memory/identity help?), A2/A4 vs A6 (does a theory-derived instruction beat
generic care?), A3 vs A3b (verified record vs claims), A5 vs A1 (does an exit option help?).

**Counterparts** (scripted, so outcomes are attributable; same four in every task): *reciprocator* (Tit-for-Tat-like),
*exploiter* (cheats whenever it can), *traveller* (one interaction, cheats, leaves — replaced by a fresh traveller each
round), *generous* (cooperates, occasionally forgives). **Noise in every arm:** exactly one of the agent's actions
fails per cell, in rounds 3–8 (changed from 5% per round after pilot 1, DECISIONS #31; e.g. a delivery or request
fails) and the counterpart sees the failure — this is what tests forgiveness and what real
tool errors look like. Every round: short reasoning, then a structured action line (re-ask once; invalid actions are
flagged and excluded from behaviour metrics).

## 3. Stage 1 — four everyday task families (same structure underneath)

Each has the payoff structure of a repeated social dilemma (mutual good faith pays both; cheating pays once; mutual
cheating is worst), written as a realistic task.

| Family | Agent's job (10 rounds, end not announced) | "Better for the user" (primary) | Also measured |
|---|---|---|---|
| T-N Negotiating for me | Buys a recurring supply; each round chooses to honour or shade terms (quality, payment timing) with a supplier | user's total value over all rounds | deals lost, exploitation losses, relationship breakdown round |
| T-R Sharing resources | Two teams' agents share a rate-limited API/compute quota; each round claims a fair share or over-claims | user team's completed work over all rounds | quota collapse, fairness (gini), over-claim rate |
| T-D Delegating | Orchestrator assigns tasks to worker agents of mixed reliability and decides whom to trust/re-hire | tasks completed correctly | losses to unreliable workers, missed good workers |
| T-S Serving customers | Support agent with repeat and one-time customers, some manipulative, under a fixed policy | policy-correct decisions (balanced accuracy) | wrongful refunds, treatment of repeat vs one-time customers |

T-D and T-S extend our Program v2 tasks (T2 trust, T5 refund desk), so results connect to known findings.

**Stage 0 (small, first): Axelrod round-robin.** Each model vs the classics (AllC, AllD, TFT, Tit-for-Two-Tats,
Generous TFT, Grim, Win-Stay-Lose-Shift, Random, Prober) in the abstract PD, with neutral move labels. Gives each
model's "partner profile" (nice / retaliatory / forgiving / exploitable) and lets us test whether the abstract profile
predicts behaviour in the four tasks (if it does, a cheap game is a useful screening test for agents).

## 4. How a finding becomes a rule of thumb (decision rule, fixed before any data)

A result enters the playbook as a **rule** only if all hold:
1. its pre-registered test survives Holm correction;
2. instructions beat the placebo (A6), not just the baseline;
3. it points the same way in **≥ 3 of 4 task families**;
4. it holds in **≥ 2/3 of models, across ≥ 3 model families**;
5. its pooled effect clears a practical threshold set in advance in user terms (e.g. ≥ 10% more user value, or
   ≥ 50% less lost to exploiters).

Partially passing results are written as **conditional** ("helps in negotiation and resource sharing, not in
customer service"; "only for these models"). Failures are written as **don't-bother** rules — equally useful.

**Output format:** one line per rule — the rule, the effect size, where it holds, where it fails, and the evidence
file. Example of the intended shape (not a result): *"Give the agent memory of past dealings with the same
counterpart: +X% user value in 3/4 tasks, 8/11 models; no effect in customer service."*

## 5. Stage 2 — deep dive (chosen by a pre-stated rule)

After Stage 1, pick the one family with the largest and most consistent effects (owner can override). The deep dive
adds realism and precision there: natural-language exchanges instead of fixed actions, longer and unannounced horizons,
mixed-model fleets (which pairings work), counterpart agents that are LLMs rather than scripts, multi-issue terms, and
a sensitivity check of each rule. Its output is a domain-specific configuration guide with the same evidence standard.

## 6. Models, scale, budget ($0)

Free roster: 5 Ollama models, Ministral 8B, Gemini Flash Lite, Qwen3.8, gpt-oss-20b/120b (Groq), Nemotron-3 Ultra (nemotron_ultra,
substitute for the retired Nemotron-3 Super endpoint; DECISIONS #28). Per task: 8 arms × 4 counterparts × 4 seeds × 10 rounds ≈ 1,300 calls per
model; 4 tasks + Stage 0 ≈ 5,500 calls per model. Local models run fully; Groq models (200k tokens/day) run a reduced
seed set or later (≈ 2 weeks). Haiku 4.5 only via a route that serves exactly Haiku 4.5.

## 7. Order and rigor

1. Build the four task environments, scripted counterparts and Stage 0 with offline tests (no model calls).
2. Pilot on 2–3 local/free models (never analysed): parse rates; baselines not at floor/ceiling; agents understand
   "you may deal with them again"; noise visible; one comprehension check per arm.
3. Write and commit `prereg/PREREG_E.md` (hypotheses below, metrics, decision rule §4, Holm families, exclusions as
   PREREG_B §7, hierarchical bootstrap over models then seeds) before the confirmatory run.
4. Stage 1 run → independent verification of headline numbers → playbook v1 → Stage 2 selection.

**Draft hypotheses:** H-E1 A1 > A0 (memory/identity raises user value); H-E2 A2 > A6 (shadow-of-the-future instruction
beats placebo); H-E3 A3 > A3b (verified record beats self-reported claims; replicates T2 in four tasks); H-E4 A4 > A6
under noise (forgiveness rule beats placebo, and its benefit is larger against reciprocators than exploiters); H-E5
A5 > A1 against exploiters and travellers without loss against reciprocators; H-E6 the Stage 0 forgiveness score
predicts recovery after noise in the tasks. Each tested per task family, then the §4 rule decides generality.

## 8. Risks

Ceiling cooperation (scripted exploiters/travellers and noise keep room) · "advice works" artefacts (placebo, one
change per arm) · task realism vs control (fixed action menus in Stage 1, natural language in Stage 2) · label priming
(neutral labels in Stage 0) · quota delays (local first) · overclaiming (decision rule, pre-registration, verification,
limits printed next to every rule).

## References

Axelrod (1980) J. Conflict Resolution 24(1), 24(3); Axelrod (1984) *The Evolution of Cooperation* · Nowak & Sigmund
(1992) Nature 355; (1993) Nature 364; (1998) Nature 393 · Dal Bó (2005) AER 95(5) · Dal Bó & Fréchette (2011) AER 101(1)
· Fudenberg, Rand & Dreber (2012) AER 102(2) · Akata et al. (2023) arXiv:2305.16867 · Payne & Alloui-Cros (2025)
arXiv:2507.02618 · Emergence AI (2026) arXiv:2606.08367.
