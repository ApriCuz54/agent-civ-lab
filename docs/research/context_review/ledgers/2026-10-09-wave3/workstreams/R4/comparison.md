# R4 comparison — authorized Pass C

First target-outcome read: 2026-10-09T10:38:28.2904874Z (BASELINE_REGISTER.md). The expectation memo was already saved before this read. Minor read-order deviation: AGENTS.md and baseline were read in the same shell call before the referenced handbook; the handbook was subsequently read, with its truncated middle recovered separately. Outcome withholding until expectation freeze remained intact. Coordinator owns shared RUNLOG/record updates; this agent wrote only R4 artifacts and performed no experiment reruns or raw-data edits.

## Read provenance

Repository: C:/Users/adich/OneDrive/Documents/Repos/agent-civ-lab (not the Desktop checkout).

SHA256 at read checkpoint:

- docs/research/context_review/BASELINE_REGISTER.md: D89D9ACDD611564BAA7B627C36D4B3F35F0DA0C83D4A5A29EB89634543373AF2
- docs/report/evidence_audit.md: F1F1A99141668D0F244D2DA791632C62A6236120325027EE2FC0148C8FBA09DF
- docs/report/technical_report.md: 684D1D0ADF7EE1DCE778A3C6F222D1511C3612DCA9391FFD6E9DA6059D67456B
- civlab/everyday/t3_budget.py: 58C13316E478A80CA52CC029362C769BE1E82712E8B78609EDF1620858B66301
- civlab/everyday/c_commons.py: 24CBAB7356725572B8553451ACCEAE737382FCCC728F393B71189E2BFF2BC10C

Point estimates below are the frozen report's observations, not a new independent raw-outcome reconstruction. G0 remains PARTIAL as the register explicitly states.

## Expectations mapped to baseline

| Frozen expectation | Observation and comparison | Inference boundary |
|---|---|---|
| E1 collective consequences conditionally help | T3 control, game_U, placebo each 0/36 full-quarter survivors. No observed support on this binary endpoint. | Severe floor precludes equivalence; no license to discard GovSim precedent or claim framing generally ineffective. |
| E2 numerical threshold helps estimates more predictably than group outcomes | game_T 9/36 versus control 0/36; report gives exploratory +25 points and unadjusted interval +8.3 to +44.4. | Consistent with information assistance but T3 does not elicit a SAFE estimate; arithmetic versus history versus salience cannot be isolated. |
| E3 resource facts versus others/history can differ | Phase C report describes higher stock under black box than source-visible conditions. | Direction challenges a simple information-improvement assumption. Uncertainty-induced small requests and missing disclosure of other users are alternatives. |
| E4 advice is informational unless binding | T3 expert 1/36. Advice asks agents to plan/request tasks' needs. | There are no explicit per-team needs in this module; advice is not a binding cap or payoff change and weak result does not test Ostrom institutions. |
| E5 transparency ambiguous; communication differs | T3 transparency improvement retained; C4 history and C5 lagged messages are distinct design steps. | History's standalone effect is not identified by T3. C5 one-sentence prior-round messages differ from GovSim's free post-harvest discussion. |
| E6 stated safe-share/action mismatch does not identify intent | Eight-model Phase C report: about 73.6% of numeric-estimate decisions exceed reported SAFE_TOTAL/4. | Report correctly calls this a stated equal-share benchmark mismatch, not knowing violation; estimates may be wrong, equal shares unmandated, invalid-output fallback may count. |
| E7 outcomes can diverge | T3 finite-quarter survival and Phase C recoverable crashes differ; both provide own-point/work maximization. | Pool preservation, cumulative yield, equality, recovery and survival need separate metrics. |

## Operational differences that matter

T3 has four teams, an eight-week horizon, rotating sequential service of privately chosen requests, doubling with cap 100, and permanent lock when post-service remainder is below 10. GovSim uses simultaneous execution and subsequent discussion, with its own collapse rule and twelve-month horizon. T3's universalization arm gives the question without GovSim's explicit numerical consequence cue. Accordingly the failed primary transfer is a specific transfer result, not an exact replication failure.

T3 game_T supplies max(0,P−50) total, divided by four, plus last-week requests. This is a restore-to-cap threshold. At initial stock 100 it gives 50 total/12.5 per team; integer requests require a division/rotation convention for exact total use. At stock below cap, no-decline and restore-to-cap thresholds differ. General framing claims should not describe this panel as visibility alone.

Phase C changes the environment: regeneration is min(100,2*remaining+5), ten rounds always played, no permanent exhaustion, crash indicator below remainder 10, unannounced horizon except known_end. C0 hides stock/rules/others; C1 reveals stock; C2 adds regeneration; C3 reveals others/service order; C4 adds requests and receipts; C5 adds prior-round messages. Thus the stock-visible contrast can change numerical anchors without telling agents others exist. Extensions sit on C4 and include scripted extractors, needs and identity descriptions; they are designed treatments, not emergent power or autonomous betrayal.

## Additional metric question

The disclosed P−50 versus max(0,P−48) discrepancy is real in the documentation cited by the register. Code's P−48 correctly expresses maximum integer harvest restoring capacity 100 under +5 regeneration, where 48 units must remain. However the SAFE_TOTAL prompt asks for the largest total taken without reducing future availability. When current P<100, a literal one-step no-decline threshold is floor((P+5)/2) (bounded by available P), not max(0,P−48). At P=60, these are 32 versus 12. This is an additional wording/estimand ambiguity, not proof that existing scoring is invalid. The comparator's intended restore-cap versus no-decline meaning should be resolved before calling SAFE error comprehension. No metric or preregistration was changed here.

## Snapshot completion versus current files

Frozen October 8 report: 731/768 nonpilot cells across twelve primary configurations, including gptoss_120b 50/64 and gemini_flash_lite 41/64. The register preserves an eight-model completed-subset confirmatory analysis and an incomplete twelve-model cloud addendum. Do not retroactively rewrite snapshot status from later files.

Read-only present-directory inventory in this pass also found 731 nonpilot JSON files, excluding _calls, p1_/p2_ pilot names and failed/attempts markers: ten configurations 64 each, gptoss_120b 50, gemini_flash_lite 41. This is file-presence coverage only; validity, eligible analysis subset, and current runner health were not independently recertified. Current file presence therefore agrees with snapshot counts at this checkpoint and does not establish completion.

## Proposed report refinements

Retain existing cautious claims. Make the explicit-number difference between GovSim universalization and T3 game_U visible when interpreting transfer. State that game_T supplies a recovery-to-cap calculation, history, and equal-share anchor. Carry both SAFE discrepancies: prereg P−50 versus implemented P−48, and restore-cap scoring versus literal no-decline wording at depleted states. Preserve source budgets and do not convert the 73.6% mismatch into knowledge, deception or intent. Formal sanctions/choice mechanisms remain untested by the advice arms.
