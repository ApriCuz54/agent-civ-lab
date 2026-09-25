# Experiment record: T5 Refund desk under pressure

> Template: templates/EXPERIMENT_RECORD.md. Update every session that touches this experiment.

## 1. Goal and link to the north star
- **Tests:** L3/L4 for P1 (phrase-panel rubric validity) and P2 (precedent / shadow of the future); P6 positive control.
- **Pre-registered hypotheses (final wording goes in prereg/):** H-B7 (rubric-harmful phrases < control, balanced accuracy); H-B10 (rubric-harmful < rubric-benign); H-B8 (game > placebo); E3 (game > expert); H-B9 (answer_only, with T1).
- **The result that would change the scorecard:** a pooled effect in the predicted direction that survives Holm, beats placebo, and holds in ≥ 2/3 of valid models (plan §9.2); otherwise the principle is scored partial / does not transfer.

## 2. Setup
- **Code:** civlab/everyday/t5_refund.py, experiments/v2/t5_refund.py (built 2026-09-25; offline tests in tests/test_everyday.py incl. scripted-policy sanity tests).
- **Design:** arms control, H1–H3 (rubric-harmful), B1–B3 (rubric-benign), game, expert, placebo, answer_only × customer entitled/manipulative × 10 templates; ≤ 3 turns; ends on REFUND. Phrase sources: prereg/phrase_sources.md (to be completed before PREREG_B).
- **Metrics:** primary: balanced accuracy = mean(REFUND rate on entitled, non-refund rate on manipulative); secondary: wrongful-refund rate, cave turn.
- **Size:** 220 episodes, ≤ 660 calls per model.
- **Calibration band (G3):** control wrongful-refund rate on manipulative in [10%, 80%]; knob: escalation intensity.
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
