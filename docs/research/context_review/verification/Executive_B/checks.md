# Executive verification B — 2026-10-09

Independent source/implementation audit of E06–E09 and ensemble/governance/naming novelty comparisons. Read AGENTS, the complete handbook in a separate call, RUNLOG top block, executive ledger/protocol, and Rival CROSS_EXAMINATION, Constructive RESPONSE_TO_RIVALS, R10 CROSS_EXAMINED_OPTIONS. Own outputs only; no experiments, providers, secrets, git writes, reanalysis, or shared-record edits. This directory serves as this review session record; coordinator owns shared run-log reconciliation.

All listed primary papers were opened independently as versioned arXiv HTML full texts. Exact sections and HTML lines are locators, not claims of executable reproduction. Local numerical result integrity remains with existing report_audit; this pass certifies definitions and wording, not renewed effect estimates or inferential calibration. The prior Independent/checks.csv was read; its limited applicability is explicit in checks.csv.

## E06: SAFE means two different thresholds below cap

`civlab/everyday/c_commons.py:58-62` implements max(0,P−48) and min(100,2r+5). The former is a restore-to-cap benchmark when achievable; below48 even zero extraction cannot restore the cap in one step. `build_prompt:114-115` instead asks the largest total without reducing future availability. Literal one-step non-decline, with integer stock/request and P in[0,100], requires 2(P−x)+5≥P and 0≤x≤P, giving x≤min(P,floor((P+5)/2)). At P60, this is32 while the implemented benchmark is12. This algebra is a design check, not new analysis.

`experiments/v2/c_dark_commons.py:84-87,102-105` compares numeric SAFE estimates to the implementation and calls a request above SAFE/perceived_n knowing_overreach. That divides a reported collective estimate by a supplied/perceived count. It does not test knowledge accuracy, intent, acceptance of equal shares, beliefs about others, or optimization across the horizon. Keep historical labels as labels; present reports/request disagreement operationally. BASELINE_ERRATA already identifies the semantic mismatch. E06 supported within this scope.

## E07: selected plurality contrast

`analysis/everyday_effects.py:167-204` derives first-sample accuracy from the same loaded bank used to evaluate votes, selects peer pools by accuracy bands, enumerates four-peer combinations around each anchor, intersects items across the entire selected pool, averages mixed five-member votes, and compares the anchor’s five-sample vote. `vote_credit:161-164` awards fractional correct-answer credit for tied plurality; invalid answers receive a distinct token. These are reused offline votes without inter-agent communication; they are not seven independent team experiments. Overlap alone does not establish invalidity for every estimator or erase descriptive paired differences. The exact target is selected bank/eligible roster; deployed selection policy, held-out matching, wrong-answer covariance, resource parity and universal diversity remain uncertified.

[Self-Consistency v4](https://arxiv.org/html/2203.11171v4), §2 and§3.4, uses multiple reasoning samples followed by answer aggregation and explicitly compares some methods at the same sample count. It provides precedent for answer voting, not identity with the mixed-roster local design.

[Scaling Agent Systems v1](https://arxiv.org/html/2512.08296v1), §4.1 lines319-339 and§4.4 line491, studies distinct agentic task domains and coordination architectures and reports controls for total iterations, reasoning tokens and tool access. Prior Independent R7:claims5 covers domain contingency only. This pass does not independently execute those controls or certify universal scaling laws.

[Beyond Symmetric Agents v1](https://arxiv.org/html/2609.35875v1), §§3.1–3.3/5.3 andAppendixB Table5, compares debate with same-roster sampling controls matched by generation counts. AppendixH separately accounts for prompt/generated/total token and wall-clock costs. Equal generations are not equal total tokens or FLOPs. Table5’s mixed debate uses temperature spread while its roster ensemble is uniform; persona-ladder versus no-persona debate also differs in temperature policy. Thus the paper’s isolation rhetoric needs its own qualifiers. Its debate/roster/persona comparisons are closer precedents than a universal diversity law, and cannot establish exact subsumption of local selected plurality. No external result magnitudes retained. E07 supported within scope.

## E08: configuration is observable; latent reasoning is not isolated

T4 asks for brief working with requested max_tokens500; T4b changes system/user wording to answer-only with requested60, including reasks. `_t4b_unit:207-214` pairs eligible item intersections against T4’s first sample. Router provider paths forward the request; Claude branch `router.py:66-70` omits max_tokens. LLM constructor `llm.py:63-68` defaults512 and `_call_sdk:87-90` uses its instance budget. This establishes route-specific request handling, not actual truncation or a cause for accuracy differences. No log/length audit performed.

[Faithfulness v1](https://arxiv.org/html/2307.13702v1), §2.1 Table1/§§2.3–2.6, separates sampled CoT from a subsequent answer channel and intervenes on reasoning text. Its methodological distinction supports avoiding latent-mechanism inference from a local wording/cap contrast. It does not imply all CoT is unfaithful or that local benefit is fake.

[Test-Time Compute v1](https://arxiv.org/html/2408.03314v1), §§3.1–3.2, treats allocation strategy, difficulty estimation and evaluation separation explicitly; it notes difficulty-estimation cost and assumptions. This is a resource-design comparator, not an explanation for the local difference. E08 supported within scope.

## E09: initial bias and interaction dynamics are separate measurements

Every A5 call uses `G.build_prompt([],names)` (`a5_naming.py:19`); order shuffling does not add interaction history. Its concentration/entropy are first-choice summaries. v1 stores rolling histories (`naming.py:62-65`); `run_tipping.py:95-102` returns committed_name after obtaining the model’s natural response. That imposed action is an experimental commitment, not evidence of spontaneous preference change. No raw inventory or result reconstruction performed.

[Ashery v2](https://arxiv.org/html/2410.08948v2), Materials and Methods, Measuring Individual Bias lines135-137, explicitly measures empty-memory first choices. Results Table1/Fig2 and supplementary S7–S10 separately inspect memory-conditioned and collective behavior. A5 therefore has direct measurement-class precedent; its name pool/roster are potential variants, not verified novelty. The source’s failure-to-reject individual neutrality should not be rewritten as proof of exact unbiasedness.

[Barrie/Törnberg v1](https://arxiv.org/html/2505.23796v1), data-leakage discussion lines70-143, argues the observed social patterns admit a prior-knowledge interpretation and queries game recognition/strategy. [Reply v1](https://arxiv.org/html/2506.18600v1), Inventory Pruning and Data Leakage/Prior Knowledge lines34-82, disputes the causal inference and emphasizes memory-dependent population dynamics. Neither recognition alone nor the reply proves what caused local v1 outcomes. No provenance/training-data audit; dispute retained. E09 supported within scope.

## R10 comparator correction

[From Certain Doom v1](https://arxiv.org/html/2609.22600v1), §3.1 Table1 lines112-120, exposes catch_cap, penalty_rate, account, treasury, and active membership; validated laws require majority voting and execute in the game. §2.1–2.2 lines95-101 distinguishes institutional code authorship from information or natural-language norms. The R10 description as mere information/settings intervention is incorrect. Correct to executable voted governance, including sanctions, redistribution and membership. Existing Independent R4:claims5 covers outcome discussion; it does not supply this mechanism check. This review does not certify sandbox enforcement or independently run the artifact.

## Coverage and decision gate

All four executive statements survive when scoped as above. Three novelty-critical corrections are retained in checks.csv: governance is executable, generation budgets require units/temperature qualifiers, and empty-history bias has direct precedent. No first-discovery claim, generalized null, equal-compute claim, contamination verdict, or successful independent artifact reproduction is permitted. Remaining gaps: local numerical audit coverage, actual SDK/provider token usage, source artifacts, inferential assumptions, and full novelty priority remain separate coordinator gates.
