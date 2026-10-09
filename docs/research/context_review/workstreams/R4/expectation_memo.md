# R4 frozen expectations — Pass A

Frozen: 2026-10-09. Outcome-withheld review. Only the neutral design description was supplied; no local repository, experiment results, baseline memo, logs, or agent trajectories were inspected. Literature outcomes are evidence, not target-study outcomes. This file is the comparison anchor and should remain unchanged when Pass B begins.

## Expectations

1. Explicit collective consequences should usually reduce over-requesting when depletion dynamics or coordination calculations are the bottleneck. Confidence: moderate. Direction is conditional; no prediction of universal success or a particular effect size (GovSim S1, section 3.4).
2. A calculated sustainable equal-share number should improve stated safe-share accuracy more reliably than it improves realized group sustainability. Confidence: moderate for arithmetic, low-to-moderate for actions. This is an inference: information can resolve computation without resolving incentives, beliefs about others, or joint coordination.
3. Resource-stock and regeneration information should help threshold estimation. Information about other users/history has ambiguous behavioral direction: it could support coordination or induce imitation of high extraction. Confidence: moderate that the distinction matters; low about the sign of the latter effect (S3).
4. Expert advice is an informational/injunctive intervention unless accompanied by binding allocations, penalties, exclusion, voting, or changed payoffs. Expect heterogeneous compliance. Confidence: moderate. Do not call advice alone an institution or enforcement mechanism.
5. Transparency/history should be tested against a null or adverse effect, not presumed sufficient. Repeated inter-agent communication has stronger precedent than one-way disclosure, but transport from human experiments to LLM agents remains uncertain (S1–S3).
6. A stated safe-share/action gap is possible even with accurate estimates. It does not identify deception, selfishness, hidden intent, or understanding of long-term strategy. Analyze the two outputs separately and consider prompt interpretation, units, threshold meaning, expectations of others, and sampling variation first.
7. Persistence, efficiency, equality, and individual survival can diverge. A low allocation is not automatically cooperation: it may underuse the pool. Confidence: high as a measurement distinction (S1, S5).

## Falsification and comparison rules

Compare treatment minus matched baseline by model, scenario, seed/run, and round; use run-level replication, not agent-round counts as independent trials. Keep request versus realized allocation distinct. Define safe share using actual regeneration law, collapse boundary, timing, population, integer rounding, and whether conserving current stock or restoring capacity is intended. For a stock B with doubling regeneration and N equal agents, B/(2N) is a continuous no-decline benchmark before rounding; it is not B/N. Do not assume the target design uses exactly these dynamics.

A robust null/adverse effect of explicit correct thresholds weakens expectation 1 for that setup; improved estimates without improved allocations supports an information/coordination distinction but not intent attribution. Sustainability gains without estimate improvement could reflect an anchor or compliance rather than improved arithmetic. Changes under history alone cannot distinguish norm formation from imitation without additional evidence. No ranking of target-study models or treatment effect magnitudes is frozen.

## Boundary

Ostrom concerns institutions embedded in ecological and social contexts, including rule-making, monitoring, sanctions, conflict resolution, and user rights. Prompt variants cover only a subset. Label findings as behavior in a specified simulation; do not infer human validity or general capability across institutions.
