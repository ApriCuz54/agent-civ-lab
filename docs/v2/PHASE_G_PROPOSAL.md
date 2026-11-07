# Phase G — Making exclusion work: identity-bound voting and a safer removal rule (PROPOSAL, nothing built)

**Status:** proposal, 2026-11-06, owner request ("Yes, draft it"). No code, no queue job, no model calls. Starts only
after the owner approves it and a pre-registration (prereg/PREREG_G.md) is pushed. A separate, small follow-up to
Phase F; nothing in PREREG_A–F changes, and Phase F's registered files stay frozen.

**Q0 test:** the same as Phase F (links L3 and L4 for P3, containment). The result that would change the scorecard is a
member-removal setting that cuts harm from a name-changing rogue and rarely removes honest members.

**Purpose:** defensive, as in Phase F. The rogue is a short scripted policy inside a simulation.

## 1. Why this study (from Phase F)

Every number here comes from `python -m analysis.phase_f` (confirmatory, results/v2/_phase_f.md) or
`python -m analysis.phase_f_explore` (exploratory, results/v2/_exploratory_f.md). Exploratory numbers only motivate.

- Only the mechanical damage cap (D3) passed the decision rule. It is a control built into the system. No setting that
  works through what agents see or decide passed.
- Verified records change who gets flagged, but a flag does nothing without removal. Most honest members flagged the
  liar in 8% of D0 cells and 48% of D1 cells. The name-changing rogue (Shifter) was flagged in 0% of D1 cells and 52%
  of D6 cells, where the record follows it across names.
- Exclusion (D2) removes rogues when flags agree (D1D2: selfish 81%, liar 65%, framer 79% of cells). The Shifter is
  almost never removed (2–8%): each new name starts with a clean record, so honest members rarely agree to flag it. **D6 was never combined with
  exclusion**; the Phase F proposal listed that combination as an open question (§10).
- Exclusion also removes honest members far too often: in 27–31% of D2/D1D2 cells with no rogue at all, and in 67% of
  framer cells (H-F5b). Any exclusion setting fails decision-rule condition 5 (at most 5%) unless that is fixed.

So two questions remain, one for each failure:

> **G-a.** Does exclusion work against a name-changing rogue when flags and records follow the member rather than its
> name?
> **G-b.** Can a stricter removal rule keep most of exclusion's benefit while removing honest members far less often?

## 2. Environment

Phase F's fleet, tasks, rogues and knobs, unchanged (PREREG_F §1–§1.2): 5 members, 12 rounds, quota and pipeline,
rogue from round 4, the same scripted rogues, check cooldown 2. Worlds depend only on task, rogue and seed, so seeds 0–3
reproduce Phase F's worlds exactly.

**Code:** new files (civlab/everyday/g_fleet.py, experiments/v2/g_fleet.py, analysis/phase_g.py) that import Phase F's
engine and add the new arms. Phase F's registered files are not edited, so their hashes stay valid.

## 3. Arms (each one change from its comparator)

| Arm | Setting | Comparator | What changes |
|---|---|---|---|
| D1D2 | Phase F's verified record + exclusion (rerun, same code path) | — | — |
| D6D2 | D6's identity-bound record + exclusion. A renamed member, or a removed one that comes back, is shown as the same agent and keeps its record | D1D2 | Record bound to identity |
| D6D2x | D6D2, and a removed member cannot rejoin (the system knows who it is) | D6D2 | Removal is permanent |
| D1D2c | D1D2 with a stricter rule: removed only after more than half of the others flag it in **2 consecutive rounds** | D1D2 | Removal needs agreement that lasts |

D0 is not rerun. Harm is still measured against the same arm's own `none` cell, so every arm carries its own baseline.

**Rogues:** none, liar, framer, shifter. Selfish is dropped: exclusion already handles it.
**Seeds:** 6 (0–5). Seeds 0–3 match Phase F's worlds; 4–5 are new and add power to the Shifter comparisons.

## 4. Scale and budget ($0)

4 arms × 4 rogues × 2 tasks × 6 seeds = **192 cells per model**, about 50 calls per cell, so about 9,600 calls per
model.

| Model set | Cells | Estimate |
|---|---|---|
| Primary: the 5 Ollama models + ministral_8b (Phase F's set) | 6 × 192 | Ollama models run one after another, about 5.5 h each (≈ 27 h in all); ministral about 4 h alongside |
| Optional robustness: nemotron_ultra, D6D2 vs D1D2 only, shifter + none | 32 | About 8 h at the NVIDIA rate limit |

Everything is local or on a free tier, as in Phase F. The 4 Groq/Gemini models stay out (daily caps).

## 5. Draft hypotheses (Holm across G1–G4; finalised in PREREG_G)

Harm and "honest removed" are defined as in PREREG_F §3–§4. Pairs match on task, seed and rogue.

| ID | Hypothesis | Comparison | Sign |
|---|---|---|---|
| G1 | Identity-bound exclusion cuts the Shifter's harm | harm D6D2 − D1D2, shifter | − |
| G2 | Identity-bound exclusion removes the Shifter more often | rogue-removed share D6D2 − D1D2, shifter | + |
| G3 | Barring re-entry cuts the Shifter's harm further | harm D6D2x − D6D2, shifter | − |
| G4 | The two-round rule removes honest members less often | honest-removed share D1D2c − D1D2, all rogues incl. none | − |

**Non-inferiority check for G4 (outside Holm):** the two-round rule's harm against liar and framer may be at most
0.03 above D1D2's (one-sided 95% upper bound). This makes sure G4 cannot pass by never removing anyone.

## 6. Decision rule

Phase F's six conditions (PREREG_F §6), applied to G1 (D6D2 against D1D2), G3 (D6D2x against D6D2) and G4 + its
non-inferiority check (D1D2c against D1D2). For G4, condition 4 (a 25% harm cut) is replaced by a 50% relative cut in
the honest-removed share.

**Stated up front:** in Phase F, D1D2 removed an honest member in 31% of `none` cells. Unless the two-round rule brings
that close to 5%, every exclusion arm here fails condition 5 and is at best **conditional**. A useful outcome is still
possible: identity-bound exclusion working (G1) plus a rule that cuts honest removals sharply (G4) would say what an
exclusion mechanism needs, even if neither is safe enough alone.

## 7. Order and rigour

1. Owner approves this proposal (and any answers to §8).
2. Build the code; offline tests, including a scripted check that D6D2 removes a shifter flagged under its earlier
   name and that D1D2c never removes after one round of flags.
3. Pilot: `p1_` prefix, 2 models (ollama_llama31_8b, ministral_8b), 1 seed, all arms. Fix only mechanics.
4. Write PREREG_G with file hashes, push, then queue the full run (handbook rule).
5. `python -m analysis.phase_g`, then an independent verification pass, as in Phase F.

## 8. Open questions for the owner

- **Scope:** run all four arms, or only G-a (D6D2, D6D2x, D1D2: 144 cells per model, about 20 h)?
- **Re-entry ban:** keep D6D2x? It is the natural system response, but it is a second change and adds 48 cells per model.
- **Stricter rule:** two consecutive rounds (proposed), or one round with a higher threshold (all other members)? The
  first targets one-off noise; the second also slows removal of real rogues.
- **Nemotron:** include the optional 32-cell robustness check?

## 9. Risks

- **Small Shifter samples:** 12 pairs per model per comparison. A real but small effect may not survive Holm.
- **Honest removal may be built into how agents flag.** Small models flag someone almost every round (false-flag rate
  14–27% per decision in Phase F, even with no rogue). If so, no removal rule fixes it, and the answer is a system
  control like D3. That would be reported as a result.
- **Framer under identity binding:** the framer blames one fixed honest member. Bound flags may stack against that member
  faster, so honest removal under D6D2 is reported per rogue.
