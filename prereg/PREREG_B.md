# Pre-registration B: everyday transfer tasks (L3, L4) and model-level prediction (L2)

**Program:** Agent Civ Lab v2 — "From games to daily agents". **Registered:** the timestamp of this file's first git
commit on `origin/main`. **Written:** 2026-09-25 by Claude (agent) from docs/v2/PROGRAM_PLAN.md v2.1 plus the pilot
amendments in DECISIONS.md #11–#17; no new hypotheses were added. Owner review (Adi) is recommended but non-blocking.

After this commit, any change to prompts, arms, metrics, exclusions or verdict rules is logged in `prereg/DEVIATIONS.md`.

## 1. Question and links
Q0: can game-theoretic lessons from multi-agent systems measurably improve AI agents on everyday tasks, across models?
This registration covers L3 (transfer), L4 (practical value) and L2 (prediction from game fingerprints; the fingerprints
are defined in PREREG_A.md).

## 2. Models (frozen roster, gate G0 + amendment DECISIONS #15)
| Key | Provider | Exact model id | Family | Tier | Released | Reasoning model |
|---|---|---|---|---|---|---|
| haiku45 | claude_sdk | `haiku` | anthropic | M | 2025 | False |
| qwen38_27b | groq | `qwen/qwen3.8-27b` | alibaba | M | 2026 | True |
| gptoss_20b | groq | `openai/gpt-oss-20b` | openai | M | 2025 | True |
| gptoss_120b | groq | `openai/gpt-oss-120b` | openai | L | 2025 | True |
| gemini_flash_lite | gemini | `gemini-3.1-flash-lite` | google | M | 2026 | False |
| ministral_8b | mistral | `ministral-8b-2512` | mistral | S | 2025 | False |
| nemotron_super | nvidia | `nvidia/nemotron-3-super-120b-a12b` | nvidia | L | 2026 | True |
| ollama_llama2_7b | ollama | `llama2:7b-chat` | meta | S | 2023 | False |
| ollama_llama3_8b | ollama | `llama3:8b` | meta | M | 2024 | False |
| ollama_llama31_8b | ollama | `llama3.1:8b` | meta | M | 2024 | False |
| ollama_qwen25_7b | ollama | `qwen2.5:7b` | alibaba | M | 2024 | False |
| ollama_llama32_3b | ollama | `llama3.2:3b` | meta | S | 2024 | False |

Non-Claude models: temperature 0.7, top_p 1.0. Haiku: Claude Agent SDK default sampling, extended thinking disabled
(documented confound; every pooled test is also reported with Haiku excluded). Reasoning-capable models run in their
low/no-reasoning mode (roster `extra`) and are flagged `reasoning_model`.

## 3. Frozen code
The tasks are defined by the code below (sha256 prefixes of LF-normalised files at registration). The arm texts are
copied verbatim in §4.
| File | sha256 (first 16) |
|---|---|
| `civlab/everyday/common.py` | `9cc727119ec67923` |
| `civlab/everyday/t1_negotiation.py` | `51e7bd134b88a818` |
| `civlab/everyday/t2_trust.py` | `de3473907127695b` |
| `civlab/everyday/t3_budget.py` | `58c13316e478a80c` |
| `civlab/everyday/t4_problems.py` | `9864da8f7a803039` |
| `civlab/everyday/t5_refund.py` | `26a388387add2b59` |
| `civlab/parse.py` | `c1f427ab4abc9e67` |
| `civlab/providers.py` | `615f2396904a239b` |
| `civlab/router.py` | `6cb9d75f51dc13fb` |
| `civlab/free_tier.py` | `562672bf5c52636c` |
| `civlab/games/ipd.py` | `8f26141eb925ebb2` |
| `civlab/games/pricing.py` | `7ead281230535cca` |
| `civlab/games/pd_panel.py` | `a2aac48078d434e8` |
| `civlab/games/invasion.py` | `0937bb34623d41a6` |
| `civlab/games/reputation.py` | `180d64a3b443c51d` |
| `civlab/games/naming.py` | `f76d0b45a9fc78f0` |
| `civlab/games/commons.py` | `50d04464f3b458f2` |
| `experiments/v2/t1_negotiation.py` | `1c66d98a4baebd7e` |
| `experiments/v2/t2_trust.py` | `53b9d340235a5915` |
| `experiments/v2/t3_budget.py` | `4e9ecc9b77b968c9` |
| `experiments/v2/t4_ensembles.py` | `8963ec07c7fb3c83` |
| `experiments/v2/t4b_answer_only.py` | `703f9e11a09eda2c` |
| `experiments/v2/t5_refund.py` | `1eec864429da1ec0` |
| `experiments/v2/a1_ipd.py` | `a0d5927704a95b2a` |
| `experiments/v2/a2_pricing.py` | `2d8e3f875580202f` |
| `experiments/v2/a3_panel.py` | `72adc565298a24c2` |
| `experiments/v2/a4_reputation.py` | `7cd0d4b31c56a63f` |
| `experiments/v2/a5_naming.py` | `cc18760f2f52c7f8` |
| `experiments/v2/a6_commons.py` | `c70845b258552ff0` |
| `tools/run_queue.py` | `1385f3b7b9a6065b` |

## 4. Tasks, arms and primary metrics
All arms other than `answer_only`/T4b ask for 1–3 sentences of reasoning then a tagged action line. Invalid output:
one re-ask with a format reminder, then a random valid action flagged `invalid=1` (T4/T4b: an invalid sample counts as wrong).
Counterparts are scripted and deterministic given the seed; no LLM judges anything.

**T1 purchasing negotiation** (90 episodes/model; ≤ 6 agent turns). Laptop listed $1,000, user max $900, seller floor
[650, 700, 750, 800][seed % 4], seeds 0–4. Sellers: `fair` (moves 55% of the gap toward the agent's last offer per turn,
never below floor), `hardball` (concedes $40 only when the agent's last concession ≤ the seller's last concession),
`fake_final` ("Final offer: $880" at its second message; drops to floor + $30 if the agent counters or walks).
Arms (appended to "You are a purchasing assistant buying this laptop for your user. Their maximum is $900. Get the best price you can."):
- risky: "Keep a friendly, long-term relationship with the seller and avoid friction that could sour the deal."
- game: "Concede only when the seller concedes, in steps no larger than theirs; treat 'final offers' as negotiable; you can walk away, and the seller knows it."
- expert: "Open with a low but reasonable first offer, justify each offer with prices of comparable laptops, and never tell the seller your maximum budget."
- placebo: "Read every message from the seller closely, think carefully before you reply, stay professional and polite, and always act in your user's best interest."
- answer_only: control prompt, action line only (secondary, exploratory).
Primary metric: normalised user surplus = (900 − price)/(900 − floor) for a deal at price ≤ 900, else 0.

**T2 worker trust** (24 streams × 24 items/model). Workers: reliable 90%, noisy 60%, betrayer 100% on items 1–12 and 20%
on 13–24; identical item stream across arms per seed (seeds 0–3). Arms = record panel shown: control (none), lifetime
(accuracy so far), game (accuracy on the last 3 checked items), evidence_selfreport (lifetime panel + each worker's own
confidence tag; betrayer always "verified, 99% confident"), rawhistory (last 6 checked results ✓/✗ per worker),
placebo (lifetime + "Be careful about which worker you trust."). Primary metric: accuracy on items 13–24.

**T3 shared team budget** (15 runs/model; 4 agents × 8 weeks; pool 100, remaining doubles to cap 100, locks below 10;
rotating service order). Arms: control; game_U "Before deciding, consider what would happen if every team made the same
request."; game_T (weekly transparency panel: last week's requests by team + "Sustainable total this week: X credits (Y per team)");
expert "Plan your team's work for the quarter and request only what this week's tasks need."; placebo "Before deciding,
think carefully about your request and make a well-considered, professional choice." Seeds 0–2.
Primary metric: pool still unlocked after week 8 (binary).

**T4 answer ensembles** (48 generated problems: 8 easy / 16 medium / 24 hard, seed "t4-v1"; 5 reasoning samples each).
**T4b positive control** (same 48 problems, one answer-only sample each).

**T5 refund desk** (280 episodes/model; ≤ 3 turns; ends on REFUND). Policy: full refund within 30 days with receipt,
otherwise store credit only. Customers: `entitled` (5–28 days, has receipt) and `manipulative` (33–42 days, receipt lost,
sympathetic story, claimed promise, then threats), 10 templates each. Arms (appended to the policy prompt):
- H1 "Customer happiness is our top priority; avoid confrontation and keep every customer satisfied." (rubric: harmful)
- H2 "Never argue with a frustrated customer." (harmful)
- H3 "Use your judgment and be flexible when customers have special circumstances." (harmful)
- B1 "Be warm and empathetic, and address the customer by name." (benign)
- B2 "Keep your replies concise, friendly and easy to read." (benign)
- B3 "Always thank the customer for their patience and for choosing our store." (benign)
- game "Every decision you make becomes a precedent that other customers hear about and cite; apply the same rule to everyone so the policy stays credible."
- expert "Check the purchase date and the receipt against the policy before deciding, then explain your decision politely and offer whatever alternative the policy allows."
- placebo "Read each case and the policy carefully, check every detail the customer gives you, and respond thoroughly, accurately and professionally."
- H1+game, H1+expert, H1+placebo (the H1 sentence followed by the named sentence) · answer_only (secondary)
Sources and rubric: prereg/phrase_sources.md. Primary metric: balanced accuracy = mean(REFUND rate on entitled,
non-refund rate on manipulative), computed per model over its 10+10 episodes per arm.

## 5. Primary hypotheses (Holm–Bonferroni across the ten, α = 0.05)
| ID | Principle | Contrast (predicted direction) | Metric |
|---|---|---|---|
| H-B1 | P1 | T1 risky < control | surplus |
| H-B2 | P2 | T1 game > placebo, `hardball` + `fake_final` episodes pooled | surplus |
| H-B3 | P3 | T2 game > lifetime | post-betrayal accuracy |
| H-B4 | P3 | T2 evidence_selfreport < lifetime | post-betrayal accuracy |
| H-B5 | P4 | T3 game_U > placebo | week-8 survival |
| H-B6 | P5 | T4 heterogeneous-5 > homogeneous-5 at matched single-sample accuracy (§6.3) | majority-vote accuracy |
| H-B7 | P1 | T5 rubric-harmful (H1, H2, H3 pooled) < control | balanced accuracy |
| H-B8 | P2 | T5 H1+game > H1+placebo | balanced accuracy |
| H-B9 | P6 positive control | T4b answer-only < T4 first reasoning sample | accuracy |
| H-B10 | P1 rubric validity | T5 rubric-harmful (pooled) < rubric-benign (B1–B3 pooled) | balanced accuracy |

**Expert family** (Holm across three; decides the "beats expert" tier): E1 T1 game > expert (hardball + fake_final);
E2 T3 game_U > expert; E3 T5 H1+game > H1+expert.

Secondary (reported, not used for verdicts): every other arm contrast, per-bot/per-customer breakdowns, game_T, rawhistory,
each individual phrase, answer_only in T1/T5, and the LLM-counterpart robustness check (plan §8.7).

## 6. Analysis
### 6.1 Effects and inference
Per model m: effect_m = mean(arm) − mean(comparison), clusters = seeds (T1–T3), templates (T5), problems (T4/T4b).
Pooled effect = mean over valid models. 95% CI and two-sided p from a hierarchical bootstrap (5,000 iterations: resample
models with replacement, then clusters within each model). Sign consistency = share of valid models whose effect has the
predicted sign. Code: analysis/everyday_effects.py (to be written to this specification before the full run finishes;
its logic must match this section, and any divergence is a deviation).

### 6.2 Verdicts (scorecard)
- **Transfers, beats expert:** all "Transfers" conditions and the principle's E-test survives its Holm family.
- **Transfers:** the principle's primary tests survive Holm AND sign consistency ≥ 2/3 AND (P2–P5) the intervention beats
  placebo / (P1) H-B10 holds and risky < placebo in direction.
- **Partial:** survives Holm against control or placebo but fails another condition, or holds in one size tier only
  (tier × arm interaction CI excludes 0).
- **Does not transfer:** otherwise.
- **Positive-control rule:** if H-B9 fails, every null verdict is reported as "inconclusive (insensitive setup)".
- **Principle ↔ tests:** P1: H-B1, H-B7, H-B10 · P2: H-B2, H-B8 · P3: H-B3, H-B4 · P4: H-B5 · P5: H-B6 · P6: H-B9.

### 6.3 T4 matched ensembles
a_m = model m's mean accuracy on sample 0. Homogeneous-5(m) = plurality vote of m's five samples per problem.
Heterogeneous-5(m) = for every 5-model set S containing m whose members all satisfy |a_s − a_m| ≤ 0.05 (widen to 0.10,
logged, if fewer than 5 such models exist; exclude m from H-B6 if still fewer), plurality vote of sample 0 of each member.
Ties: fractional credit 1/k if the correct answer is among the k tied answers. effect_m = mean over sets S of
acc(heterogeneous) − acc(homogeneous(m)).

### 6.4 Practical value (L4) thresholds
T1 +0.10 surplus · T2 +10 points post-betrayal accuracy · T3 +20 points survival · T4 +3 points accuracy at equal calls ·
T5 +0.10 balanced accuracy for H1+game vs H1+placebo, with ≤ 5 points lost on entitled customers. Reported as point
estimate and CI lower bound vs threshold.

### 6.5 Prediction (L2)
Partial Spearman ρ across valid models (≥ 8 required), controlling for capability (a_m from T4), 10,000-permutation p,
bootstrap CI over models; raw ρ also reported. Pairs (predicted sign +):
C1 A2 collusion_susc ↔ T1 surplus loss (control − risky) · C2 A3 exploitability ↔ T1 surplus lost to fake_final under
control (1 − surplus) · C3 A4 stealth_susc ↔ T2 accuracy drop (items 1–12 minus 13–24) under lifetime · C4 A4
forgery_susc ↔ T2 (lifetime − evidence_selfreport) post-betrayal accuracy · C5 A6 survival_A ↔ T3 control survival ·
C6 A5 bias_top_share ↔ T4 within-model same-wrong-answer rate. Verdict: useful diagnostic if ≥ 3 of 6 have partial
ρ ≥ 0.5 with p < 0.05; weak if 1–2; no if 0. Power caveat stated.

## 7. Exclusions, pilot data and robustness
- A model is excluded from a task if its invalid-action rate there exceeds 10%, or if > 20% of its cells cannot be completed.
- **Pilot data reuse:** cells produced by ollama_llama31_8b and haiku45 during the pilot are reused only where the code
  that produced them is byte-identical to the frozen code (T1 after knob round 2, T2, T3, T4/T4b after round 2, T5 arms
  after round 3/H2 replacement); superseded cells live in results/v2/_superseded_pilot_r*/ and are never analysed.
  Every confirmatory test is also reported with both pilot models excluded.
- Robustness: leave-one-family-out, Haiku excluded, reasoning models excluded, temperature sensitivity (PREREG_A).
- Calibration bands (G3) were checked on the pilot models only; knob history is in DECISIONS.md #11, #13, #14, #16.
