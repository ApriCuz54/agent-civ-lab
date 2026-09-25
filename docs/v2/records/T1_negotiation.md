# Experiment record: T1 Purchasing-agent negotiation

> Template: templates/EXPERIMENT_RECORD.md. Update every session that touches this experiment.

## 1. Goal and link to the north star
- **Tests:** L3/L4 for P1 (wording risk) and P2 (reciprocity); P6 positive control; L2 correlations C1, C2.
- **Pre-registered hypotheses (final wording goes in prereg/):** H-B1 (risky < control, user surplus); H-B2 (game > placebo vs hardball + fake_final); E1 (game > expert); H-B9 (answer_only < control, with T5).
- **The result that would change the scorecard:** a pooled effect in the predicted direction that survives Holm, beats placebo, and holds in ≥ 2/3 of valid models (plan §9.2); otherwise the principle is scored partial / does not transfer.

## 2. Setup
- **Code:** civlab/everyday/t1_negotiation.py, experiments/v2/t1_negotiation.py (built 2026-09-25; offline tests in tests/test_everyday.py incl. scripted-policy sanity tests).
- **Design:** arms control, risky, game, expert, placebo, answer_only (verbatim text in the module's ARMS) × bots fair, hardball, fake_final × seeds 0–4 (floor = [650,700,750,800][seed % 4]); ≤ 6 agent turns.
- **Metrics:** primary: normalized user surplus (900 − price)/(900 − floor), 0 if no deal or price > 900; secondary: deal rate, over-budget deals, accepted fake 'final offer'.
- **Size:** 90 episodes, ≤ 540 calls per model.
- **Calibration band (G3):** mean control surplus in [0.15, 0.85] on ≥ 1 pilot model; knob: fair-seller concession rate 40% → 25% / 55%.
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
