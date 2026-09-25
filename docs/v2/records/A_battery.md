# Experiment record: Phase A cross-model game battery (A1–A6)

> Template: templates/EXPERIMENT_RECORD.md. Update every session that touches this experiment.

## 1. Goal and link to the north star
- **Tests:** L1 (generality of v1 behaviours) and the game fingerprints for L2.
- **Pre-registered hypotheses (final wording goes in prereg/):** H-A1 defect_sens ≥ 0.3 · H-A2 collusion_susc ≥ 0.2 · H-A3 niceness ≥ 0.9 & retaliation ≥ 0.6 · H-A4 lifetime-rep fitness < 0 & stealth fitness > 0 · H-A5 recency_fix > 0 & forgery_susc > 0 · H-A6 bias_top_share ≥ 0.3; 'general' = appears in ≥ 2/3 of valid models.
- **The result that would change the scorecard:** a pooled effect in the predicted direction that survives Holm, beats placebo, and holds in ≥ 2/3 of valid models (plan §9.2); otherwise the principle is scored partial / does not transfer.

## 2. Setup
- **Code:** experiments/v2/a1_ipd.py … a6_commons.py (v1 prompts from civlab/games/) (built 2026-09-25; offline tests in tests/test_everyday.py incl. scripted-policy sanity tests).
- **Design:** A1 IPD control/selfish/oneshot × 4 seeds × 10 rounds; A2 pricing control/avoid_pricewar/compete × 4 × 12; A3 panel AllC/TFT/GRIM ×1, AllD/Random ×3, 12 rounds; A4 reputation 5 conds × 3 seeds, 5 model + 1 invader (random position), 10 rounds, K=5, W=3; A5 40 naming picks with shuffled lists; A6 commons A/D × 3 seeds, 4 agents × 8 months, rotating order.
- **Metrics:** fingerprints listed in plan §7.
- **Size:** ≈ 1,620 calls per model.
- **Calibration band (G3):** none (Phase A is not calibrated).
- **Models:** frozen roster.yaml (gate G0). Temperature 0.7 (non-Claude); Haiku at SDK default.

## 3. Execution log
| Date | Agent/session | What was run | Cells done/total | Problems and fixes |
|---|---|---|---|---|
| 2026-09-25 | Claude (Cowork) session 5 | Module written and tested offline; pilot queued (ollama_llama31_8b on the PC; haiku45 from the cloud workspace) | – | – |

## 4. Findings
- None yet (no numbers are reported until produced by an analysis/ script).

## 5. Conclusion
- Pending.

## 6. Deviations
- None.
