# Decision log (Program v2)

Adi writes each entry **in his own words** (plan §0.5 rule 5). Claude may draft the context line,
but the "why" is Adi's. Format: what was decided, the alternatives, why, date.

| # | Date | Decision | Alternatives considered | Why (Adi) |
|---|---|---|---|---|
| 1 | 2026-09-24 | Phase B (everyday tasks) gets queue priority over Phase A (games) | A first (v2.0 order) | |
| 2 | 2026-09-24 | Every game-derived arm is compared with a placebo **and** a domain-expert arm | placebo only | |
| 3 | 2026-09-24 | T5 uses a pre-classified phrase panel sourced from real prompts | one hand-written risky phrase | |
| 4 | 2026-09-24 | Non-Claude models at temperature 0.7; Haiku at SDK default (documented confound) | T=1.0 everywhere; T=0 | |
| 5 | 2026-09-24 | Invalid output: one re-ask, then a random valid action flagged invalid; >10% invalid excludes the model from that experiment | v1 default-to-C parser | |
