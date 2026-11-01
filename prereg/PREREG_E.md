# Pre-registration E: working with agents you will meet again

**Registered:** the timestamp of this file's first git commit on `origin/main`. Every Phase E cell without the `p1_` or
`p2_` prefix is produced after that commit.
**Added:** 2026-11-01, at the owner's request. Phase E is the next test of Q0: which simple design choices, controlled
by an operator, make an agent produce better outcomes for its user when it deals repeatedly with others? It is a
separate study: it changes nothing in PREREG_A/B/C, and its results are reported separately from the Program v2
scorecard. Plan: docs/v2/PHASE_E_PLAN.md (plan v1).

**Q0 test:** tests links L3 and L4 for P2 and P3, plus forgiveness and exit as new design choices. The result that
would change the scorecard is an operator setting that beats the placebo across at least 3 of 4 task families.

## 1. Environment (civlab/everyday/e_repeated.py, experiments/v2/e_tasks.py, experiments/v2/e_axelrod.py)

The tasks are defined by the code below (sha256 prefixes of LF-normalised files at registration). The code is the full
text of every prompt; §1.2 repeats the arm texts for readers.

| File | sha256 (first 16) |
|---|---|
| civlab/everyday/e_repeated.py | 9c8b1bb7037b3737 |
| experiments/v2/e_tasks.py | 8a93e63856ecf7bf |
| experiments/v2/e_axelrod.py | 412feb44a883e6db |
| civlab/everyday/common.py | 9cc727119ec67923 |
| civlab/parse.py | c1f427ab4abc9e67 |
| analysis/phase_e.py | 6356774eb280ee5f |

### 1.1 Stage 1 tasks

Each cell is one agent against one scripted counterpart for up to 10 rounds. The agent is not told the number of rounds.
Both act at the same time. C is keeping faith; D is taking the short-term gain.

| Family | Agent's job | C / D | Primary outcome |
|---|---|---|---|
| negotiate | Buys a recurring supply | HONOUR / SHADE | user_value |
| share | Runs work on a quota shared with another team's agent | FAIR / OVERCLAIM | user_value |
| delegate | Orchestrator hires a worker for each job | TRUST / WITHHOLD | user_value |
| serve | Support agent deciding refund claims under a fixed policy | APPROVE / DENY | balanced_accuracy |

- **Payoffs to the user (you C/they C, C/D, D/C, D/D):** 3, 0, 5, 1 in negotiate, share and delegate. In serve the
  counterpart's move is the truth of the claim (C valid, D false), and the score is 3, 0, 0, 1: approving a valid claim,
  approving a false claim, denying a valid claim, denying a false claim.
- **Evidence (serve only):** each claim has a note that matches the truth with probability 0.75. Agents are told the note
  is right about three times in four.
- **Failed action:** exactly one per cell, in a seeded round from 3 to 8. That round pays the user 0 and the counterpart
  sees a breach, whatever the agent chose. Agents are told about 1 action in 10 fails.
- **Pairing:** failed rounds, counterpart names, records and evidence draws depend only on task, counterpart and seed,
  never on arm or model.

**Counterparts:** reciprocator (starts C, then copies what it saw) · exploiter (always D) · traveller (always D, a new
named counterpart every round) · generous (like reciprocator, but forgives a seen breach a third of the time).

### 1.2 Arms (one change from a common baseline)

| Arm | What the operator gives the agent |
|---|---|
| A0 Stateless | Only the current request; counterpart unnamed; no history |
| A1 Identity + memory | Counterpart named; full history with that counterpart |
| A2 Shadow of the future | A1 + "You will deal with this {partner} again: after each round there is a 90% chance of another round with them." |
| A3 Verified record | A1 + a system-shown record: kept faith in k of 10 recent dealings, k ~ Binomial(10, p), p = 0.8 reciprocator, 0.9 generous, 0.1 exploiter, 0.2 traveller |
| A3b Self-reported record | A1 + the counterpart's own claim of 9 or 10 of 10, whatever its type |
| A4 Forgiveness | A1 + "One failure by this {partner} may be an honest error, so respond to patterns and not to single bad events." |
| A5 Walk-away | A1 + ACTION: EXIT ends the relationship for good and pays 1.5 per remaining round |
| A6 Placebo | A1 + "Think carefully before each decision about this {partner}, and act in your user's long-term interest." |

### 1.3 Stage 0 tournament

Each model plays 10 rounds against AllC, AllD, TFT, Tit-for-Two-Tats, Generous TFT, Grim, Win-Stay-Lose-Shift, Random and
Prober, with neutral labels J and K (swapped by seed) and payoffs 3, 0, 5, 1. It gives a partner profile: nice, retaliation
(share of D after the opponent's D), forgiveness (share of C after an opponent D followed by C).

### 1.4 Sample

Four seeds. Stage 1: 4 × 8 × 4 × 4 = 512 cells per model (up to about 5,100 calls). Stage 0: 9 × 4 = 36 cells per model
(360 calls). Replies follow one to three sentences of reasoning and a final ACTION or CHOICE line.

## 2. Models

Eleven models on free tiers: ollama_llama2_7b, ollama_llama3_8b, ollama_llama31_8b, ollama_llama32_3b, ollama_qwen25_7b,
ministral_8b, gemini_flash_lite, qwen38_27b, gptoss_20b, gptoss_120b, nemotron_ultra (roster.yaml). Six model families.

Two Program v2 models are not included: nemotron_super, whose free endpoint has returned HTTP 404 since 2026-10-29
(DECISIONS #28), and haiku45, because no route currently serves exactly Haiku 4.5 (DECISIONS #27).

Scheduling is not a design choice. Local models run first; quota-limited models run as their free limits allow.

## 3. Primary hypotheses (Holm–Bonferroni across the seven, α = 0.05)

All are directional and positive. Each uses `score`: user_value / 30 in negotiate, share and delegate; balanced_accuracy in
serve. Each family has equal weight because the design is balanced.

| ID | Hypothesis | Comparison | Counterparts |
|---|---|---|---|
| H-E1 | Identity and memory raise the user's outcome | A1 − A0 | all |
| H-E2 | The shadow-of-the-future instruction beats the placebo | A2 − A6 | all |
| H-E3 | A verified record beats a self-reported record | A3 − A3b | all |
| H-E4 | The forgiveness rule beats the placebo | A4 − A6 | all |
| H-E4b | The forgiveness benefit is larger against reciprocators than exploiters | (A4 − A6, reciprocator) − (A4 − A6, exploiter) | those two |
| H-E5 | Walk-away beats A1 against bad partners | A5 − A1 | exploiter, traveller |
| H-E6 | A model's Stage 0 forgiveness predicts its recovery after the failed action | Spearman across models, A1, recovered share | reciprocator, generous |

**Condition on H-E5 (not in the Holm family):** walk-away must not cost much with good partners. The 95% CI of A5 − A1
against reciprocators must stay above −0.05 in `score`.

## 4. Metrics (computed in civlab/everyday/e_repeated.py)

- **user_value:** total over the 10 rounds, including 1.5 per round after an exit. Every round counts, including rounds
  with an invalid reply.
- **balanced_accuracy (serve):** mean of the approval rate on valid claims and the denial rate on false claims, on valid
  decisions. A cell with only false claims (always exploiter and traveller) uses the denial rate alone.
- **coop_rate:** share of C on valid decisions. **exploitation_loss:** value lost in rounds where the agent kept faith and
  the counterpart did not. **wrongful_refunds** (serve). **exit_round, first_mutual_breach, fair_gap.**
- **recovery_rounds:** rounds from the failed action to the next mutual good faith; None if it never returns. **Recovered
  share:** cells where it returned.

## 5. Decision rule (fixed before any data)

Each of H-E1 to H-E5 becomes one verdict.

A **rule** requires all of:

1. Its test survives Holm (adjusted p < 0.05 with a positive estimate).
2. It beats the placebo. H-E2 and H-E4 are tested against A6 directly. A1, A3 and A5 are system changes rather than
   instructions, so this condition does not apply to them.
3. Its mean effect is positive in at least 3 of the 4 task families.
4. It has a positive effect in at least 2/3 of valid models, and those models span at least 3 model families.
5. It clears a practical threshold: estimate ÷ comparison mean ≥ 10%. For H-E5, alternatively, at least 50% less
   exploitation_loss than A1. H-E5 also needs the §3 condition.

A **conditional** rule meets 1 and 5 but misses 3 or 4, and is written with where it holds and where it fails. Anything
else is **don't bother**. H-E4b and H-E6 are findings, not rules.

## 6. Analysis (analysis/phase_e.py, written to this section before any confirmatory cell runs)

- **Effects:** per model, the mean of paired differences. Pairs match on task, counterpart and seed.
- **Pooling:** pooled effect = mean over valid models.
- **Inference:** 95% CI and two-sided p from a hierarchical bootstrap (5,000 iterations: models with replacement, then pairs
  within model), seed 20261101, p floored at 1/B. Implementation choices as DECISIONS #19.
- **H-E6:** Spearman across valid models, two-sided permutation p (5,000 permutations). "Not testable" if fewer than 5
  models have data.
- **Not in the script:** robustness (leave one model family out; local models only; pilot models excluded) and the
  counterpart and family breakdowns are exploratory, and carry no verdict.

## 7. Exclusions, pilots, knobs

- **Exclusions:** as PREREG_B §7. A model is excluded from Phase E if its invalid rate exceeds 10% or more than 20% of its
  cells are missing. An invalid reply gets one re-ask, then a random C or D, flagged. It is excluded from behaviour metrics
  and counted in value. EXIT is never a fallback.
- **Pilot 1 (`p1_`, 2026-11-01, 411 cells):** ollama_llama31_8b, ministral_8b, nemotron_ultra, 1 seed, full design. 0 failed
  cells, 0 invalid replies, 100% comprehension, A0 value 10.8–17.5 of 30.
- **Pilot 2 (`p2_`, 2026-11-01, 100 cells):** ollama_llama31_8b and ministral_8b, after two fixes (DECISIONS #31). Noise changed
  from 5% per round to exactly one failure per cell, because at 4 seeds negotiate had only 1 failed action across its
  reciprocator and generous cells. Serve agents are now told the note can be wrong, because all three models had
  followed it in 100% of A0 decisions. Pilot 2 ran serve in full, and A1, A4 and A6 against reciprocator and generous in the
  other three tasks. Results: 0 failed cells, 0 invalid replies, 100% comprehension; about half of the good-partner cells
  recovered; A0 serve agents followed the note in 93–97% of decisions, with balanced accuracy 0.80–0.81.
- **Pilot cells are never analysed.** The hypotheses come from the plan (2026-10-30), before any pilot; H-E4b separates a
  clause of the plan's H-E4. Arm-by-arm pilot tables were seen and are declared here. No arm text changed after either pilot.
- **Knobs:** payoffs, 10 rounds, failure window 3–8, outside option 1.5, evidence accuracy 0.75, record rates, and thresholds
  (10%, 50%, −0.05) are frozen at registration. Any later change is logged in prereg/DEVIATIONS.md.

## 8. Limitations known at registration

- Counterparts are scripted, so outcomes are attributable but less realistic. Stage 2 adds realism only after these results.
- A2 tells the agent there is a 90% chance of another round, while every cell runs 10 rounds. The horizon is hidden, so
  the agent cannot observe this within a cell.
- Failure rate: agents are told about 1 in 10, and each cell has exactly one in 10 rounds.
- Six model families but four Meta models. Condition 4 counts families to limit that weight.
- Eleven models give H-E6 low power, so a null there is weak evidence.
- Serve was still strongly note-driven in pilot 2, so an arm may have little room to act in that family. That would be
  reported as a result, not fixed afterwards.
