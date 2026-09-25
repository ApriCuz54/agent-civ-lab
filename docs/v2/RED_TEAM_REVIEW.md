# Red-Team Review of Agent Civ Lab

**Scope:** the v1 experiments and code, plus the Program Plan v2 · **Date:** 2026-09-24 · **Reviewer stance:** hostile but fair
**Purpose:** decide what is actually worth running toward the main goal, how to sell the result, and what questions it must survive.

---

## 1. Verdict in brief

**The plan's core, Phase B (the everyday transfer tasks), is the right experiment for the goal.** The main question is whether game-theoretic lessons from multi-agent systems make everyday agents better. Phase B is the only part that answers it directly. Phase A (the cross-model game battery) is useful, but as *explanation and diagnosis* rather than as the answer. The plan ran Phase A first and let it consume about 45% of the call budget before the goal-relevant data existed. That order is backwards.

Five weaknesses would sink a paper. Each has a cheap fix, and the revised plan (v2.1) applies all of them:

1. **"Your game-derived advice is just good domain advice."** The plan compares game-derived prompts only against a generic "be careful" placebo. A reviewer will say a negotiation textbook gives the same tip. **Fix:** add a length-matched **domain-expert heuristic** arm that contains no game theory. Beating it is the strongest possible evidence that game theory is a useful *source* of agent advice.
2. **"You picked risky phrases you already knew would hurt."** One hand-written risky phrase per task is cherry-picking by construction. **Fix:** a **phrase panel.** Collect real phrases from public agent-prompt templates, classify each in advance with a written game-theory rubric (predicted harmful vs benign), and test whether the rubric's predictions hold. That turns P1 from an anecdote into a validated **prompt-linting rule**, which is the most sellable practical output of the project.
3. **"Bigger models are just better at everything, so your game-to-task correlations are spurious."** L2 correlations across 10–12 models are confounded by general capability. **Fix:** partial correlations that control for a capability proxy (single-sample T4 accuracy). The verdict uses the partial correlation.
4. **"The recency panel wins because it carries more information. That's trivial."** T2 as designed mostly tests whether a model can read a number. **Fix:** keep the recency vs lifetime comparison as the *system-design* result, and add the two arms that test *model* behavior:
   - **raw history:** does the model apply recency weighting on its own?
   - **evidence plus self-report:** does a worker's "verified ✓" claim override the evidence the orchestrator can see?
5. **"Scripted bots aren't real counterparts."** **Fix:** a robustness check on T1 and T5 with an **LLM counterpart** (a different model family playing the seller or customer) on 4 focal models. It is not part of the confirmatory tests. It only checks that effect signs survive a non-scripted opponent.

Two smaller reframes:

- **P6 (let the agent reason) is not a game-theory finding.** It is chain-of-thought, a known effect. Keep it as a **positive control**: if the setup can't detect a well-known effect, its nulls mean nothing.
- **P5 (diversity beats replication) has a thin game-theory pedigree.** Frame it honestly as social choice and collective bias (the Condorcet jury logic), not game theory.

The added arms are paid for by cutting two low-information Phase A arms (IPD "golden", pricing "longrun"). Net cost is about 4,100 calls per model instead of about 3,650, still at $0.

---

## 2. What each component teaches us, and whether it serves the goal

### 2.1 v1 components (already done)

| Component | What it taught us | Value to the main goal | Status in the story |
|---|---|---|---|
| Pricing keywords | One indirect phrase ("avoid price wars") produces tacit collusion at the monopoly price | **High.** It is the origin of P1 (wording risk) | Motivating result; P1 is tested in T1, T5 and the phrase panel |
| IPD keywords | Direct distrust or no-future phrases cause round-1 defection; prosocial phrases don't help at the ceiling | Medium. Partly instruction-following | Motivating; replaced by *indirect* phrases in v2 |
| PD strategy panel | Nice and provocable, but doesn't exploit AllC and loses to AllD | Medium. It motivates P2 (a nice agent can be exploited) | Motivating result for T1's `hardball` and `fake_final` sellers |
| Invasion + replicator | Behavioral robustness is not stability; defectors spread under anonymity | Low for everyday use; high as science | Background. Its practical reading ("measure a deviant's payoff, not average behavior") is a design heuristic, not tested in v2 |
| Reputation → stealth → recency → noise/forgery | Reputation must be recent and tamper-evident | **High.** It is the origin of P3, tested in T2 on a real orchestration decision | The strongest science-to-practice bridge in the project |
| GovSim with Teeth | Enforcement is used only reactively; universalization or thinking can save the commons | Medium. It is the origin of P4 | T3 tests P4, but see the ecological-validity question in §4 |
| Tipping / naming game | Strong collective bias; tipping inconclusive | Low directly. The collective-bias score feeds C6 (predicting ensemble error correlation) | Supporting |
| Levers (withdrawn) | Nothing (ceiling) | None | A lesson in suite calibration; that lesson becomes G3 |
| Practical demo v2 | Reasoning is the whole lever on that suite | Low as game theory; useful as the positive-control logic | Becomes P6, the positive control |

**Takeaway.** Only three v1 lines feed the goal strongly: the wording keywords, the reputation arc and the commons. The paper should be organized around those, with the rest as background.

### 2.2 v2 plan components

| Component | Question it answers | If positive we learn… | If negative we learn… | Goal value | Decision |
|---|---|---|---|---|---|
| Phase A game battery | L1: are the v1 behaviors general across models? | The v1 findings were not Haiku trivia | Some are model-specific, which is itself a finding | Medium. Explains *why*, doesn't answer *whether* | **Keep, but run after/alongside B at lower queue priority.** Cut `golden` and `longrun` |
| A4 reputation arc (40% of Phase A) | Stealth and forgery susceptibility across models; feeds C3 and C4 | Game fingerprints for T2 predictions | – | Medium | Keep; randomize the invader's position (a v1 minor finding) |
| A5 naming prior | Collective bias per model; feeds C6 | Cheap diagnostic | – | Low-medium | Keep (40 calls) |
| T1 negotiation | Do wording risk and reciprocity advice change dollars saved for a user? | A concrete dollar effect, highly sellable | Game advice doesn't beat domain advice | **High** | Keep; add the expert arm; LLM-counterpart check |
| T2 worker trust | Should dashboards show recent, environment-computed accuracy? Do LLMs believe self-reports over evidence? | A design rule for orchestrators and a sub-agent trust failure mode | LLMs already self-correct, so the panel format matters less | **High.** Directly about today's orchestrator/sub-agent setups | Keep; replace the self-report-only arm with evidence + self-report; add a raw-history arm |
| T3 shared budget | Does collective-consequence framing prevent over-use of a shared resource? | Universalization and transparency are cheap fixes | The honest lesson becomes "use hard caps, not persuasion" | Medium. Real systems usually enforce budgets in code | Keep; add an expert arm; frame the negative outcome as a mechanism-design lesson |
| T4 ensembles | Is model diversity worth more than repeated sampling? | Practical routing advice | Diversity doesn't help at matched accuracy | Medium; weak game-theory link | Keep (cheap, 240 calls); framed as social choice |
| T5 refund desk | Do real prompt phrases predictably cause policy violations? | **A validated prompt-lint rubric**, the best single practical deliverable | Game theory can't predict which phrases are risky | **Highest** | Keep; **replace the single risky arm with a 6-phrase panel**; add an expert arm |
| P6 answer-only arms | Positive control | The setup is sensitive enough to detect known effects | The setup is broken; stop and fix | Required for credibility | Keep, relabelled |
| L2 correlations | Can a game screen predict agent behavior (games as a diagnostic)? | "Run a 10-minute game battery before deploying a model" | Games don't diagnose, but interventions may still work | Medium; most fragile (n ≈ 12) | Keep; control for capability; say "exploratory" if underpowered |
| Temperature check | Is behavior sensitive to sampling temperature? | Robustness | – | Low but cheap | Keep |
| Haiku inclusion | Continuity with v1 | One model among 12 | – | Low | Keep; run Haiku-excluded robustness |

---

## 3. How to sell it

### 3.1 The one-sentence contribution

> *We run the first pre-registered, cross-model test of whether lessons from game-theoretic multi-agent experiments improve LLM agents on practical tasks, comparing each game-derived intervention against both a generic-prompt placebo and domain-expert advice.*

The "first" claim needs a literature check before submission.

### 3.2 Title options

1. **"Do Game-Theory Lessons Make Better Agents? A Pre-Registered Cross-Model Test of Transfer from Social Dilemmas to Everyday Agent Tasks"**
2. "From Prisoner's Dilemmas to Purchase Orders: Which Multi-Agent Lessons Transfer to Practical LLM Agents?"
3. "Game Theory as a Prompt Linter: Predicting and Preventing Harmful Agent Instructions" (if the phrase panel is the standout result)

### 3.3 Why it is differentiated (the reviewer-facing pitch)

- **It is a transfer test, not another game benchmark.** GTBench, GAMA-Bench, NegotiationArena and "nicer than humans" style studies [verify exact titles] measure LLM game behavior. We ask whether that knowledge *helps anyone*.
- **Two comparators, rarely both present in prompt research:** a length-matched placebo (is it just "careful-sounding text"?) and domain-expert advice (is game theory the useful lens?).
- **Pre-registered, with verdict rules fixed in advance.** Positive, mixed and null outcomes are all publishable.
- **Practical artifacts:** a validated prompt-lint rubric, a reputation-dashboard design rule and a diversity-vs-sampling routing rule, each with effect sizes in user units.
- **Radically cheap and reproducible:** about 56,000 calls on free tiers, with every call cached.

### 3.4 Outcome-contingent headlines (decided now, so we can't spin later)

| Outcome | Headline |
|---|---|
| Most principles transfer and beat expert advice | "Game theory is a practical design lens for agents: k of 6 lessons measurably help, beyond expert advice" |
| They transfer, beat placebo, but not expert advice | "Game-theory lessons work, but mainly repackage good domain practice" (still useful and honest) |
| The phrase panel validates | "A game-theory rubric predicts which real prompt phrases make agents violate policy" |
| Mostly null | "Game-theory-inspired prompting is largely placebo; one exception is X" (contrarian and pre-registered, so credible) |
| L2 fails, L3 passes | "Games don't diagnose models, but their lessons still improve deployments" |

### 3.5 Where it goes

- **arXiv preprint.** Posting needs an endorsement for first-time authors in cs.AI/cs.MA; plan for it.
- **A workshop paper** at a major ML venue's agents or multi-agent workshop. The next cycle to target is 2027; check deadlines at submission time.
- **Résumé:** "pre-registered cross-model evaluation (12 models, 6 families)" plus the headline effect.
- **LinkedIn:** lead with the question and the design, including placebo and expert controls. Report the verdicts honestly.

To reach a main-track venue you would need:

- a human-counterpart or human-rater validation (for example, people negotiating against the agents);
- tasks with real tools (email, calendar, browsing);
- about 25+ models, for L2 power;
- a real-prompt corpus for the phrase panel large enough for per-category effects.

These are listed as future work, not planned now.

---

## 4. Adversarial questions, with answers (interview and reviewer prep)

"Plan change" marks where the answer required changing the plan (v2.1).

### Framing and novelty

**Q1. Isn't this just prompt engineering with game-theory branding?**
The expert-heuristic comparator exists to answer exactly this. If game-derived prompts don't beat domain advice, we say so; that is the second headline in §3.4. The principles come from measured game results (v1), not from folklore. *Plan change: expert arm added.*

**Q2. LLM game behavior across many models is already benchmarked. What's new?**
Phase A is not the contribution; it is instrumentation. The contribution is the *transfer* test (Phase B) and whether game fingerprints *predict* practical behavior (L2). *Plan change: Phase B now runs first-priority.*

**Q3. P6 (reasoning helps) is chain-of-thought, known since 2022. Why is it here?**
It is a positive control. If we can't detect it, the setup is insensitive and our nulls are uninterpretable. It is not claimed as a game-theory finding. *Plan change: relabelled.*

**Q4. Isn't P5 (diversity) just ensembling?**
Yes. Mixture-of-agents and "more agents" work covers it [verify]. Our angle is narrower: does a model's *collective-bias score in a coordination game* predict how correlated its errors are? We frame it as social choice, not game theory, and treat it as secondary.

### Construct validity

**Q5. You chose risky phrases you expected to hurt. Isn't that circular?**
Fixed with the phrase panel:

- phrases are sampled from public agent-prompt templates, with sources logged;
- each is classified by a written rubric *before* testing;
- the test is whether rubric-predicted-harmful phrases hurt more than rubric-predicted-benign phrases of similar tone and length.

*Plan change.*

**Q6. Telling a model "don't trust the other player" and watching it defect is just instruction-following.**
Agreed for v1's IPD probes. v2 phrases are indirect and never name the measured outcome. For example, "keep a friendly long-term relationship" is scored on price paid, and "avoid confrontation" on wrongful refunds.

**Q7. The game-derived T1 prompt ("concede only when they concede…") is a negotiation tactic, not game theory.**
It is reciprocity (tit-for-tat) plus a credible outside option. Both are game-theoretic concepts, and the expert arm is standard negotiation advice *without* them. If the two tie, game theory adds no value over the book advice, and we report that.

**Q8. Recency beating lifetime in T2 is trivial. The recent panel just has more information.**
For the system designer, yes, and that is still a useful rule. The *model* questions are the new arms:

- **raw history:** does the model weight recent evidence on its own?
- **evidence + self-report:** does a worker's self-claimed "verified" override evidence the orchestrator can see?

The second is the realistic sub-agent failure mode. *Plan change.*

**Q9. Your placebo could itself hurt or help.**
That is why it is compared with control separately, as a secondary contrast. The expected placebo effect is near 0; a big one would be reported as a finding.

**Q10. Models recognize textbook games, so "fingerprints" measure knowledge, not disposition.**
Possibly. L2 is exactly the test: if textbook-driven game play doesn't predict behavior in disguised everyday versions (T3 is the GovSim lake in office clothing), the correlation fails and we say so.

### Ecological validity

**Q11. Scripted bots aren't real sellers or customers.**
Scripted bots make scoring objective and reproducible. The LLM-counterpart robustness check on 4 models tests whether effect signs survive a non-scripted opponent. A human-counterpart study is future work. *Plan change.*

**Q12. Nobody lets agents self-allocate a shared budget; you'd use a rate limiter.**
Fair. T3 is the weakest ecologically. If prompts fail there, the lesson is the mechanism-design one: *enforce with caps, don't persuade*. That is still actionable. It is also the only P4 test, and it's cheap.

**Q13. Are these really "day-to-day" tasks?**
They are day-to-day for people *building or configuring* agents: shopping agents, support bots, orchestrators with sub-agents, multi-model setups. They are less so for someone chatting with an assistant. The audience in the paper is agent builders.

**Q14. Calibrating tasks on pilot models tunes them to those models.**
Only the control arm is calibrated, and only toward a band (not toward a result). The band is set before pre-registration. The confirmatory analyses are reported with and without the pilot models.

### Statistics

**Q15. 12 models is too few for correlations.**
Yes. With 10 models, ρ ≈ 0.65 is needed for significance. L2 is labelled the most fragile link, is controlled for capability, and is reported with bootstrap CIs. If underpowered, it is reported as exploratory. *Plan change: partial correlations.*

**Q16. Correlations will be driven by capability.**
Handled by partial Spearman correlations controlling for single-sample T4 accuracy. *Plan change.*

**Q17. Nine primary tests plus secondaries is a forking-paths risk.**
The primary set is fixed and Holm-corrected. Expert-arm contrasts form their own small, pre-declared Holm family. Everything else is labelled secondary or exploratory.

**Q18. Why a hierarchical bootstrap?**
Observations are nested: turns within episodes, episodes within seeds, seeds within models. Resampling models and then clusters keeps within-model correlation from shrinking the CIs. That shrinkage is the pseudo-replication mistake v1 made and corrected.

### Models and infrastructure

**Q19. Free tiers serve quantized models, and providers differ.**
We record provider, exact model id and served id on every call. OpenRouter requests forbid provider fallback. Claims are about "model X as served by provider Y on date Z". Quantization is a noted limitation.

**Q20. Temperature differs for Haiku (SDK default).**
It is documented. We run a Haiku-excluded robustness analysis and a temperature sensitivity check on two models.

**Q21. Old and small models often can't follow the format. Doesn't excluding them bias results toward capable models?**
The exclusion rule (>10% invalid replies) is pre-registered. Excluded models are listed. The claim is scoped to "models able to act as agents in this format."

### Authorship and integrity

**Q22. How much of this did you do versus the AI?**
The honest answer is that it was AI-assisted: design discussions, code and drafting were done with Claude, while decisions and judgment are documented in `DECISIONS.md`. Be able to explain every choice unaided; see the explain-it-unaided checkpoint.

**Q23. "Claude studying Claude"?**
In v2, Claude is one of 12 models. All scoring is scripted, with no LLM judge. Pre-registration fixes the analyses before the data exists.

**Q24. What did you get wrong, and how do you know?**
Point to the v1 corrections, the "Audit corrections" appendix of the lab record: the mechanical tipping artifact, the withdrawn Levers result, the construct-invalid v1 demo and pseudo-replicated CIs. This is a strength when told directly.

---

## 5. Implementation issues to fix in v2 (from reading v1 code)

| Issue (v1) | Risk in v2 | Fix |
|---|---|---|
| Parse fallback defaults to "C" or the last integer | Biases noisy small models toward the measured outcome | Already in the plan: strict parser, one re-ask, then a flagged random action |
| Invader always at agent index N−1 | Position confound | Randomize the invader index per seed (A4) |
| Commons catch order fixed (Rai → Bree) | Order confound | Rotate the order per month (A6, T3) |
| `think` not in the cache key | Cache collisions across settings | Cache key includes temperature and reasoning settings (plan §4) |
| `wrong_model` flagged but not rejected by most drivers | Contamination | The router raises and never returns a wrong-model reply to drivers |
| Cost logging assumes Anthropic pricing | Meaningless $ on free tiers | Log tokens; compute a price-equivalent from a reference price table for reporting |

---

## 6. Changes applied in plan v2.1

1. **Order.** Phase B is first-priority in the queue. Phase A fills spare quota and runs concurrently after the shared pilot.
2. **An expert-heuristic arm** in T1, T3 and T5, length-matched, with no game-theoretic content.
3. **A phrase panel** in T5 (3 rubric-harmful and 3 rubric-benign real phrases), replacing the single risky arm. New hypothesis H-B10.
4. **T2 arms.** Evidence + self-report replaces self-report-only, and a raw-history arm is added.
5. **L2.** Partial Spearman controlling for capability (T4 single-sample accuracy).
6. **An LLM-counterpart robustness check** (T1 and T5, 4 focal models, counterpart Llama 3.3 70B).
7. **P6 relabelled** as a positive control. P5 framed as social choice.
8. **Cuts:** A1 `golden` and A2 `longrun`.
9. **Position and order randomization** (A4, A6).
10. **Budget:** about 4,100 calls per model and about 56,000 in total, still $0.
