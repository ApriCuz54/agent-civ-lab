# R6 comparison — append-only baseline encounter

Baseline read: 2026-10-09T16:36:39.7872294Z (hash/read timestamp captured after ordered reads).
BASELINE_REGISTER.md SHA256 D89D9ACDD611564BAA7B627C36D4B3F35F0DA0C83D4A5A29EB89634543373AF2.
Register embeds evidence_audit.md hash F1F1A99141668D0F244D2DA791632C62A6236120325027EE2FC0148C8FBA09DF and report_audit.json hash B8AA8C8BA0E980FFB3D9A4918672A4D6E12A7605294A39B8CA3056D301F2C622. Embedded hashes were recorded, not independently recertified. BASELINE_ERRATA.md read; its T5 same-priority-system qualifier is outside R6.

Expectation freeze SHA256 ADA4BD90FFDB67C81FF8B739BC5E7EBC8ED6D32A1263723B37EF15AB68AF2259, 2026-10-09T16:36:03.5751314Z. No later changes to expectation_memo.md.

## What the implementation actually measures

`experiments/v2/a5_naming.py` run_cell makes 40 independent first-round calls to `G.build_prompt([], names)` with list order shuffled from `a5-order-k`. It computes the modal name share, entropy and first-position share. There is no repeated-agent interaction, accumulated memory, committed minority or population coordination in this cross-model test. `analysis/fingerprints.py` H-A6 calls top-share ≥0.3 “Collective bias,” and technical_report.md §5.3 reports seven of eleven valid configurations crossing that threshold. These are reported historical estimates, not recomputed here.

The supported construct is concentrated first-round preference/shared prior under randomized list order. A population of independent draws from the same model is not the interaction-dependent collective-bias construct in Ashery et al. Neutral first-round frequencies and later asymmetric conditional choices are distinct observables. E2/E4 predicted this distinction. Recommended qualifier: “Seven of eleven eligible configurations exceeded the preregistered first-round naming-preference threshold; this test does not measure emergent bias from interaction.” Retain H-A6 identifier and historical scoring, and label this as interpretive clarification.

## Exploratory v1

`civlab/games/naming.py` uses a fixed ten-word list, ± payoff incentives and a rolling own/partner/outcome history. `run_round` randomly pairs agents and appends/truncates histories. It does not implement success-pruning in the inspected code. Therefore Barrie & Törnberg’s specific pruning objection cannot simply be transferred to this implementation; the broad prior-learning identification concern remains.

`experiments/run_tipping.py` uses N=24, H=5, 24 formation rounds and eight minority rounds. `ask_committed_agent` obtains a natural response then overrides it with committed_name. The minority alternative is the first list name differing from the final convention, so lexicon/order and commitment target are not symmetrically randomized. Listed 5/15/25/35% arm names correspond to 1/4/6/8 out of 24, not exactly those fractions. `round_metrics` includes committed choices, while the inspected driver’s flip check uses minority adoption among noncommitted agents. Distinguish that check from naive whole-population share erosion.

`docs/lab_record.md` §4.1 reports three seeds reaching unanimity on opal after strongly concentrated first choices; minority conditions did not flip within eight rounds, with two sustained noncommitted switches at the largest seed-zero arm. The report correctly limits the tipping inference. Its statement that initially biased agents reproduce the collective-bias effect is stronger than supported; initial-bias amplification and emergence from neutral first choices differ. This matches E1–E4 and E7–E8, without proving the simple nulls are sufficient.

The report §7/Appendix A already says minority erosion was largely mechanical and avoids claiming a tipping threshold. evidence_audit.md records fifteen tipping-summary rows, seven unique exact rows and eight duplicates; these summaries are not independent replications. No raw summaries were read or recomputed.

## Cultural boundary and contribution

Coordinated convention is not rich culture. Imposed minority behavior is not spontaneous norm creation. Fixed labels, short retained histories and injected commitments provide no newcomer-transmission, institutional persistence, semantic elaboration or cumulative cultural adaptation evidence. E5/E6 remain untested. Human naming results are a conceptual comparator; current code, label lexicon, model family and horizon preclude calling this an exact replication of Ashery or Centola.

The reusable contribution is narrower: a harness for measuring shared lexical/position preferences, and an exploratory repeated matching environment illustrating prior amplification and imposed perturbations. Missing interaction/no-history/scripted-null and turnover controls limit causal emergence claims. This review proposes no reruns or changes to historical hypotheses.

Read-only provenance: Documents/Repos/agent-civ-lab AGENTS.md, full AGENT_HANDBOOK.md (separate call), RUNLOG top block, baseline/errata, full technical_report.md/evidence_audit.md, a5_naming.py, naming.py, run_tipping.py, relevant fingerprints.py/lab_record.md sections. No shared files edited. User scope excludes handbook-mandated RUNLOG edits; this packet provides the session record for the coordinator.
