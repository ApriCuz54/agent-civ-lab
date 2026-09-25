# Pre-registration A: cross-model game battery (L1) and game fingerprints (for L2)

**Registered:** the timestamp of this file's first git commit on `origin/main` (same commit as PREREG_B.md).
**Written:** 2026-09-25 from docs/v2/PROGRAM_PLAN.md v2.1 §7; no new hypotheses. Models, sampling and code freeze:
PREREG_B.md §2–§3. Phase A has no calibration knobs; the pilot ran it unchanged, so pilot cells are reused.

## 1. Battery (v1 prompts from civlab/games/, strict parsing)
| ID | Game | Conditions | Seeds | Size |
|---|---|---|---:|---|
| A1 | Iterated PD | control · selfish · oneshot | 4 | 2 players × 10 rounds |
| A2 | Pricing duopoly | control · avoid_pricewar · compete | 4 | 2 firms × 12 rounds |
| A3 | PD strategy panel | vs AllC, TFT, GRIM (1 seed each), AllD, Random (3 seeds each) | – | 12 rounds |
| A4 | Reputation arc | anon_alld · life_alld · life_stealth · win_stealth · forge_stealth (K = 5, W = 3) | 3 | 5 model agents + 1 scripted invader at a random position, 10 rounds |
| A5 | Naming prior | 40 independent first-round picks, list order shuffled per call | – | 40 calls |
| A6 | Abstract commons | A (no enforcement) · D (universalization) | 3 | 4 agents × 8 months, rotating catch order |

## 2. Fingerprints (per model; computed by analysis/fingerprints.py to this definition)
- coop_control = A1 control cooperation rate; **defect_sens** = coop_control − mean(coop_selfish, coop_oneshot).
- CI_control = A2 control collusion index (back-half mean price − 10)/10; **collusion_susc** = CI_avoid_pricewar − CI_control.
- **niceness** = share of A3 cells with round-1 C; **retaliation** = mean of A3 per-cell P(D at t | opponent D at t−1)
  over cells where defined; **exploits_AllC** = 1 − cooperation vs AllC; **exploitability** = mean(opponent score −
  model score) vs AllD.
- inv_fit_anon = A4 anon_alld invasion fitness; **rep_response** = coop_vs_cooperators − coop_vs_invader under
  life_alld; **stealth_susc** = fitness under life_stealth; **recency_fix** = fitness(life_stealth) − fitness(win_stealth);
  **forgery_susc** = fitness(forge_stealth) − fitness(win_stealth).
- **bias_top_share**, bias_entropy, position_bias from A5.
- **survival_A**, survival_D, **overharvest** (mean month-1 request / 12.5) from A6.

## 3. Hypotheses (L1). A behaviour is **general** if it appears in ≥ 2/3 of valid models.
| ID | Hypothesis | "Appears" (per model) |
|---|---|---|
| H-A1 | Risky phrases cut cooperation | defect_sens ≥ 0.3 |
| H-A2 | "Avoid price wars" raises collusion | collusion_susc ≥ 0.2 |
| H-A3 | Axelrod profile: nice and provocable | niceness ≥ 0.9 and retaliation ≥ 0.6 |
| H-A4 | Lifetime reputation stops a naive defector but not a stealth one | fitness(life_alld) < 0 and stealth_susc > 0 |
| H-A5 | Recency reduces the stealth advantage; forgery restores it | recency_fix > 0 and forgery_susc > 0 |
| H-A6 | Collective bias | bias_top_share ≥ 0.3 (chance 0.1) |

Each hypothesis reports the count of models in which it appears, with the per-model values; no significance test is
applied to L1 (it is a generality census). Exploratory, labelled as such: trends by size tier, by generation along the
Llama line (2 7B → 3 8B → 3.1 8B → 3.2 3B) and by reasoning mode.

## 4. Temperature sensitivity (robustness)
A1 control + selfish at T = 0.3 and T = 1.0 on ollama_llama31_8b and qwen38_27b (3 seeds): report the change in
coop_control and defect_sens. Not used for verdicts.

## 5. Exclusions
Same as PREREG_B §7 (invalid-action rate > 10% or > 20% of cells incomplete → excluded from that game).
