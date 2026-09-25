# Experiment record: T4 Answer ensembles: replication vs diversity

> Template: templates/EXPERIMENT_RECORD.md. Update every session that touches this experiment.

## 1. Goal and link to the north star
- **Tests:** L3/L4 for P5 (diversity; social-choice lineage); L2 correlation C6 (with A5); capability proxy for all L2 partial correlations.
- **Pre-registered hypotheses (final wording goes in prereg/):** H-B6 (heterogeneous-5 > homogeneous-5 at matched single-sample accuracy).
- **The result that would change the scorecard:** a pooled effect in the predicted direction that survives Holm, beats placebo, and holds in ≥ 2/3 of valid models (plan §9.2); otherwise the principle is scored partial / does not transfer.

## 2. Setup
- **Code:** civlab/everyday/t4_problems.py, experiments/v2/t4_ensembles.py (built 2026-09-25; offline tests in tests/test_everyday.py incl. scripted-policy sanity tests).
- **Design:** 48 generated problems (16 easy / 16 medium / 16 hard, seed 't4-v1'), 5 samples each, brief working, ANSWER line; ensembles built offline.
- **Metrics:** primary: heterogeneous-5 minus homogeneous-5 accuracy at matched single-sample accuracy (±5 pts); secondary: within- vs between-model same-wrong-answer rate.
- **Size:** 48 cells, 240 calls per model.
- **Calibration band (G3):** pooled single-sample accuracy in [0.35, 0.85]; knob: easy/medium/hard mix.
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
