# Experiment record: <ID and name, e.g. T5 Refund desk under pressure>

> One file per experiment in `docs/v2/records/`. Written so that a stranger with only this repo can
> understand, reproduce and judge it. Update it every session that touches the experiment.

## 1. Goal and link to the north star
- **Tests:** link L_ (plan §0.3) for principle P_ (plan §0.4).
- **The result that would change the scorecard:** …
- **Pre-registered hypotheses:** H-… (copy the exact wording from `prereg/PREREG_B.md`).

## 2. Setup
- **Code:** `experiments/v2/<module>.py`, bots `civlab/everyday/<…>.py`, commit `<hash>`.
- **Models:** roster keys and exact model ids (from `roster.yaml`), temperature, reasoning settings.
- **Arms and exact prompt text:** (verbatim, or a pointer to the frozen text in `PREREG_B.md`).
- **Scenario parameters:** seeds, counts, calibration knob values.
- **Metrics:** primary and secondary, with definitions.
- **Expected calls and time:** …

## 3. Execution log (append-only, newest last)
| Date | Agent/session | What was run (queue job, models) | Cells done/total | Problems and fixes |
|---|---|---|---|---|

## 4. Findings
- Tables and figures produced by `analysis/…` (never hand-typed numbers). Include per-model effects,
  pooled effects with CIs, sign consistency, invalid-reply rates, exclusions applied.

## 5. Conclusion
- Verdict per hypothesis (supported / not supported / inconclusive), in one sentence each.
- What it means for Q0 (which scorecard cell changes and why).
- Limitations specific to this experiment.

## 6. Deviations
- Any change after pre-registration, with the `prereg/DEVIATIONS.md` id.
