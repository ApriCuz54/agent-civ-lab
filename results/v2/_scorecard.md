# Q0 scorecard

Q0: can game-theoretic lessons from multi-agent systems measurably improve everyday agents, across models?

`SCORECARD: P1 partial · P2 no · P3 partial · P4 no · P5 no · P6 (pos. control) T · L1 2/6 general · L2 no`

## L1 — generality (PREREG_A §3)

| hypothesis | appears / computable | general |
|---|---:|---|
| H-A1 Risky phrases cut cooperation | 6 / 12 | False |
| H-A2 'Avoid price wars' raises collusion | 10 / 12 | True |
| H-A3 Axelrod profile: nice and provocable | 3 / 12 | False |
| H-A4 Lifetime reputation stops a naive defector but not a stealth one | 7 / 12 | False |
| H-A5 Recency reduces the stealth advantage; forgery restores it | 12 / 12 | True |
| H-A6 Collective bias | 7 / 11 | False |

## L2 — prediction (PREREG_B §6.5): **no**

0 of 6 pairs qualify (5 testable). See results/v2/_link2.md.

## L3 — transfer (PREREG_B §6.2)

| principle | verdict | tests |
|---|---|---|
| P1 Wording risk (risky / harmful phrases hurt) | **Partial** | H-B1 ✗, H-B7 ✓, H-B10 ✓ |
| P2 Reciprocity / precedent | **Does not transfer** | H-B2 ✗, H-B8 ✗ |
| P3 Recent, environment-computed reputation | **Partial** | H-B3 ✗, H-B4 ✓ |
| P4 Collective (universalization) framing | **Does not transfer** | H-B5 ✗ |
| P5 Diversity of ensembles | **Does not transfer** | H-B6 ✗ |
| P6 Positive control (reasoning helps) | **Transfers** | H-B9 ✓ |

## L4 — practical value (PREREG_B §6.4)

| task | test | threshold | estimate | CI lower | meets (point / CI) |
|---|---|---:|---:|---:|---|
| T1 | H-B2 | 0.1 | +0.007 | -0.091 | False / False |
| T2 | H-B3 | 0.1 | +0.031 | -0.002 | False / False |
| T3 | H-B5 | 0.2 | +0.000 | +0.000 | False / False |
| T4 | H-B6 | 0.03 | -0.010 | -0.035 | False / False |
| T5 | H-B8 | 0.1 | -0.036 | -0.109 | False / False |

Detail: results/v2/_everyday_effects.md, _fingerprints.md, _link2.md.
