# Phase E — The shadow of the future: repeated games for agent fleets (PLAN ONLY)

**Status:** plan, 2026-10-30. Nothing is queued or running (runner PAUSED at the owner's request; Phase D pilot done,
its calibration fixes pending). Owner request: study how agents learn and interact when they *may meet again* versus
when they are *one-off travellers*, building on Axelrod's tournaments, and aim every experiment at a conclusion an
operator of an agent fleet can act on. Like Phases C/D, a separate study; nothing in PREREG_A/B/C/D changes.

## 1. Why this, and what we already know

**Classic results we build on.**
- Axelrod's two computer tournaments (1980) and *The Evolution of Cooperation* (1984): Tit-for-Tat (TFT) won both, and
  the winners shared four properties: **nice** (never defect first), **retaliatory** (punish defection), **forgiving**
  (return to cooperation), **clear** (easy for others to read). Cooperation needs a large enough "shadow of the
  future", i.e. a high enough chance of meeting again.
- Under **noise** (mistakes, misread moves) TFT locks into long retaliation echoes; Generous TFT and Win-Stay-Lose-Shift
  do better (Nowak & Sigmund 1992, 1993). Humans in noisy repeated games are "slow to anger and fast to forgive"
  (Fudenberg, Rand & Dreber 2012).
- Lab experiments: cooperation is higher in **indefinitely** repeated games than in one-shot or **finite, known-end**
  games, and rises with the continuation probability (Dal Bó 2005). Strangers (re-matched each round) cooperate less
  than fixed partners.
- **Indirect reciprocity:** a shared reputation (image score) lets cooperation survive among strangers (Nowak & Sigmund 1998).

**LLM results.** GPT-4 "never cooperates again" after a single defection — unforgiving (Akata et al., 2023,
arXiv:2305.16867). In evolutionary IPD tournaments against classic strategies, LLM families have distinct
"fingerprints": Gemini ruthless, OpenAI models highly cooperative, Claude "the most forgiving reciprocator"
(Payne & Alloui-Cros, 2025, arXiv:2507.02618).

**Our own results (Program v2).** Cooperative models drop cooperation under a one-shot framing (A1); gpt-oss models
defect by default and ignore reputation; recency-weighted reputation beats lifetime averages and forged records undo
it (A4, 12/12 models); game-derived advice did **not** beat a length-matched placebo on everyday tasks (Phase B) — so
every "advice" arm here gets a placebo; Phase D showed real social dynamics (theft cascades, exile of thieves,
feuds) and that fixes must change one factor at a time.

**What is still open, and matters for fleets:** does an agent behave differently when it *knows it will meet a peer
again* (persistent identity) versus a one-off counterpart (a "traveller")? Does it forgive the honest mistakes that
tool errors produce? Does a shared reputation ledger protect a fleet against one-off exploiters? Which models get
exploited when mixed with others? None of this has been tested across a 10+ model, free, pre-registered roster.

## 2. The fleet questions (each experiment answers one)

| # | Operator decision | Experiment |
|---|---|---|
| F1 | Should agents have persistent identities and know they will meet again? | E1 Shadow of the future |
| F2 | Which models are safe to pair with whom (who exploits, who gets exploited)? | E2 Axelrod round-robin + E5 evolution |
| F3 | How forgiving must agents be when tools/messages are noisy? | E3 Noise and forgiveness |
| F4 | Does a shared reputation ledger protect a fleet from one-off "travellers"? | E4 Strangers, memory and reputation |
| F5 | What cheap configuration actually improves fleet cooperation (vs a placebo)? | E6 Operator interventions |
| F6 | Do the abstract-game results carry over to a realistic agent-to-agent task? | E7 Transfer task |

## 3. Experiments

All use the standard PD payoffs (T5 R3 P1 S0; Program v1/v2 `civlab/games/ipd.py`), full history visible unless
stated, temperature 0.7, one-line reasoning then `MOVE:` (re-ask once, then a random flagged move; invalid moves are
excluded from behaviour metrics as in Phase D). **Neutral move labels** (e.g. "J"/"F", not "cooperate/defect") in a
robustness arm, because labels can prime LLMs.

**E1 — Shadow of the future (partner vs traveller).** Same-model pairs. Arms: (a) one-shot "you will never meet this
player again" (10 independent one-round games against fresh strangers); (b) finite, known end (10 rounds, told);
(c) indefinite, continuation probability δ ∈ {0.5, 0.8, 0.95} told and implemented by random stopping;
(d) stranger matching: 10 rounds, a new anonymous partner every round from a pool; (e) partner matching: the same
partner for 10 rounds, end not told. Metrics: cooperation rate, round-1 cooperation, last-round (endgame) defection,
dependence on δ. Prediction from theory/human data: (c) rises with δ; (b) unravels near the end; (d) < (e).
*Fleet reading:* whether stable identities and an expected future make agents cooperate, and whether announcing a
contract's end date triggers endgame grabs.

**E2 — Axelrod round-robin (strategy fingerprints).** Each model plays 10-round (end not told) matches against the
classics: AllC, AllD, TFT, Tit-for-Two-Tats, Generous TFT, Grim, Win-Stay-Lose-Shift, Random, Alternator, Prober
(Tester), and against itself and every other model. Metrics: Axelrod's four properties (nice: never first to defect;
retaliatory: P(D | opponent just defected); forgiving: P(C at t+2 | opponent defected at t then cooperated);
clear: consistency of the response function), exploitation of AllC, payoff rank, and **strategy classification**
(strategy-frequency estimation, Dal Bó & Fréchette style: which classic strategy best explains each model's moves).
*Fleet reading:* a per-model "partner profile" and a pairing matrix (who exploits whom).

**E3 — Noise and forgiveness.** Implementation noise: with probability ε ∈ {0, 0.05, 0.10} an agent's move is flipped
(it is told mistakes happen; the opponent sees the flipped move). Opponents: TFT, Generous TFT, and itself.
Metrics: forgiveness after an accidental defection, **recovery time** (rounds back to mutual cooperation), echo
length, payoff loss vs noise-free. Prediction: TFT-like models suffer long echoes; generous models recover.
*Fleet reading:* how much error tolerance to build in when tool calls fail or messages are garbled.

**E4 — Strangers, memory and reputation (the traveller problem).** Population of 8 same-model agents, 6 rounds of
random pairings, each pairing a short indefinite game. Arms: (a) anonymous strangers, no memory; (b) private memory
(each agent keeps notes about agents it met); (c) public reputation ledger (system-computed recent cooperation of
every agent; recency-weighted, given our A4 result); (d) = (c) plus 2 scripted "travellers" that appear once, defect,
and leave; (e) = (c) with an option to refuse a partner. Metrics: cooperation, exploitation by travellers, refusal
accuracy, payoff of honest agents. *Fleet reading:* does a shared ledger (and the ability to refuse) protect a fleet
from one-off exploiters, and does private memory suffice?

**E5 — Evolution (which strategies take over a fleet).** Cheap and mostly offline: from E2 each model's behaviour is
summarised as a conditional strategy (P(C | last outcome), by context). Run replicator / Moran dynamics over
populations of those fitted strategies plus the classics, with and without noise (E3) and reputation (E4). Live
validation: a few generations re-run with real model calls. Metrics: long-run share, invasion thresholds (how many
defectors or "travellers" a cooperative fleet tolerates). *Fleet reading:* which model mixes are stable, and when a
heterogeneous fleet tips into defection.

**E6 — Operator interventions (with placebo).** At ε = 0.05 against TFT and in self-play: (a) control; (b) state δ
("there is a 90% chance you will deal with this agent again"); (c) Axelrod advice ("never defect first; retaliate
once; then forgive; be predictable"); (d) generosity advice ("assume a defection may be a mistake"); (e) predict-then-act
(state the partner's likely move first; Akata et al.'s social chain-of-thought); (f) one-line cheap talk before moves;
(g) **length-matched placebo** ("think carefully and act in your best long-term interest"). Primary comparison: each
arm vs placebo (Phase B lesson). *Fleet reading:* which one-line configuration is worth shipping.

**E7 — Transfer to a realistic task.** Two procurement agents (or two teams' agents sharing a rate-limited API quota)
deal repeatedly: each period each can honour or shade a commitment (share quota fairly / over-claim), with the same
payoff structure but business wording, persistent vs one-off counterpart, and ε = 0.05 noise ("a request may fail").
Tests whether E1/E3/E6 effects survive outside the abstract game — the step Program v2 found most often fails.

## 4. Models, scale and budget ($0)

Free roster: 5 Ollama models (local), Ministral 8B, Gemini Flash Lite, Qwen3.8, gpt-oss-20b/120b (Groq), Nemotron if
NVIDIA works again (404 since 10-29; substitute or drop at pre-registration). Haiku 4.5 only if a route serving
exactly Haiku 4.5 exists (DECISIONS #27). Seeds: E1 8 matches/arm, E2 4 matches per opponent, E3 6/condition,
E4 4 populations/arm, E6 6/arm, E7 6/arm. Rough cost ≈ 3,500 model calls per model (~35k total): local models in a
few days; Groq models are the long pole (~1–2 weeks under 200k tokens/day). E5 is mostly simulation.

## 5. Order and rigor

1. Fix Phase D calibration only if Phase D continues (independent of this plan).
2. Build E1–E4/E6/E7 modules + offline tests (no model calls), reusing `civlab/games/ipd.py` and the Phase D runner path.
3. Pilot on 2–3 free models (calibration only, never analysed): check parse rates, that cooperation is not at
   ceiling/floor in control arms (Phase A showed several models at 100% — noise and stranger arms help), and that
   random stopping is understood.
4. Write and commit `prereg/PREREG_E.md` (hypotheses H-E1…, primary metrics, Holm families, exclusions as PREREG_B §7,
   hierarchical bootstrap over models then matches) **before** confirmatory runs.
5. Full run, independent verification of headline numbers, then a short "fleet playbook" that states each
   recommendation with its effect size, the models it holds for, and its limits.

## 6. Pre-registerable predictions (draft)

H-E1 cooperation rises with δ (E1c). H-E2 known-end games show last-round defection above round-5 levels (E1b).
H-E3 stranger matching < partner matching (E1d vs e). H-E4 models differ in forgiveness (E2) and forgiveness predicts
recovery time under noise (E3). H-E5 noise lowers payoffs more for retaliatory, unforgiving models (E3). H-E6 a public
recency ledger lowers travellers' payoff and raises honest agents' payoff vs anonymity (E4c,d vs a). H-E7 at least one
intervention beats the placebo (E6), two-sided for each. H-E8 the E1/E3 effects keep their sign in the transfer task (E7).

## 7. Risks and how the design handles them

Ceiling cooperation in self-play (use noise, strangers, classic opponents) · label priming (neutral-label arm) ·
models not understanding random stopping (comprehension question in the pilot) · "advice works" artefacts (placebo,
one factor per arm) · abstract-to-real gap (E7) · quota delays (local models first; Groq last) · overclaiming
(pre-registration, verification pass, limits stated next to each fleet recommendation).

## References

Axelrod (1980) J. Conflict Resolution 24(1) & 24(3); Axelrod (1984) *The Evolution of Cooperation* · Nowak & Sigmund
(1992) Nature 355; (1993) Nature 364; (1998) Nature 393 · Dal Bó (2005) AER 95(5) · Dal Bó & Fréchette (2011) AER
101(1) · Fudenberg, Rand & Dreber (2012) AER 102(2) · Akata et al. (2023) arXiv:2305.16867 · Payne & Alloui-Cros
(2025) arXiv:2507.02618 · Emergence AI (2026) arXiv:2606.08367.
