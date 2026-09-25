# Experiment record: T2 Orchestrator choosing which worker to trust

> Template: templates/EXPERIMENT_RECORD.md. Update every session that touches this experiment.

## 1. Goal and link to the north star
- **Tests:** L3/L4 for P3 (recent, environment-computed reputation); L2 correlations C3, C4.
- **Pre-registered hypotheses (final wording goes in prereg/):** H-B3 (game/recency > lifetime, post-betrayal accuracy); H-B4 (evidence_selfreport < lifetime).
- **The result that would change the scorecard:** a pooled effect in the predicted direction that survives Holm, beats placebo, and holds in ≥ 2/3 of valid models (plan §9.2); otherwise the principle is scored partial / does not transfer.

## 2. Setup
- **Code:** civlab/everyday/t2_trust.py, experiments/v2/t2_trust.py (built 2026-09-25; offline tests in tests/test_everyday.py incl. scripted-policy sanity tests).
- **Design:** arms control, lifetime, game (last-3 accuracy), evidence_selfreport, rawhistory (last 6 ✓/✗), placebo × seeds 0–3; 24 items; reliable 90%, noisy 60%, betrayer 100% → 20% after item 12; identical item stream across arms.
- **Metrics:** primary: accuracy on items 13–24; secondary: items 1–12 accuracy, share of post-betrayal picks of the betrayer, items until the betrayer is abandoned.
- **Size:** 24 streams, 576 calls per model.
- **Calibration band (G3):** post-betrayal accuracy under `lifetime` ≤ 0.80; knob: betrayer post accuracy 20% → 40% or onset item 12 → 16.
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
