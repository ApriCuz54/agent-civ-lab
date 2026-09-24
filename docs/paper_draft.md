# Wording, Reasoning, and Reputation: Practical Lessons from LLM Agents in Social Dilemmas

**Rough draft, v0.1 (2026-09-23).** Author: Adi. Research assistance and harness engineering: Claude.  
*All empirical results are from a single model, Claude Haiku 4.5 (`claude-haiku-4-5-20251001`), with extended thinking disabled unless stated. Cross-model replication is future work. References marked [verify] need checking against the primary source before submission.*  
---

## Abstract

Language-model agents are increasingly deployed to negotiate, price, bid, coordinate, and police one another, yet most guidance on instructing them comes from single-agent benchmarks. We ask whether classic social-dilemma games can serve as cheap diagnostic instruments that yield *actionable* guidance for people who deploy agents. Using a resumable, cost-logged harness, we ran fourteen experiments on Claude Haiku 4.5: 15,348 model calls at a total API-equivalent cost of $37.20. The experiments covered a pricing duopoly, the iterated Prisoner's Dilemma, an Axelrod-style strategy panel, population invasion, replicator dynamics, reputation under recency weighting, noise and forgery, a naming game, a common-pool resource, and a before/after transfer demo on a checkable task suite.

We report five findings.

1. **Risk from wording is asymmetric.** A single innocuous sentence ("avoid destructive price wars") takes two pricing agents from near-competitive pricing to the exact joint-monopoly price (collusion index 0.24 → 0.96, 8 seeds, Holm-corrected p < 0.001). "Do not trust the other player" collapses Prisoner's Dilemma cooperation from 1.00 to 0.10, with defection on round 1. Eleven prosocial or anti-collusion phrasings, by contrast, produce no measurable change above an already-good baseline.
2. **Behavioral cooperation is not evolutionary stability.** The model's cooperation is nice, reciprocal and provocable. It survives a lone defector behaviorally, but under explicit imitation dynamics defection spreads when agents are anonymous (defector share 12.5% → 54%).
3. **Reputation works only if it is timely and authenticated.** A public record neutralizes naive defectors (invasion fitness +28 → −16). A lifetime average is gamed by trust-then-betray invaders (+13.6). A three-round recency window closes that hole (≈0), tolerates heavy observation noise at a welfare cost, and fails completely under forgery (+14.6).
4. **On the day-to-day task, allowing reasoning was the whole lever.** Answer-only prompting scored 60%, while "show brief working" scored 100%. Personas, a verification pass and three-agent majority voting added nothing once reasoning was allowed, and voting cost 3×.
5. **Deliberation changes collective outcomes.** Agents given enforcement tools used them only retaliatorily and depleted a commons, except when prompted to universalize or when extended thinking was on.

We translate these findings into seven practical rules for agent deployment, and five methodological lessons for anyone running LLM social simulations on a budget.

---

## 1. Introduction

Multi-agent LLM systems are moving from research demos into production: procurement bots bargain with vendor bots, pricing agents react to competitors, orchestrators delegate to sub-agents, and moderation agents police other agents. At the same time, a growing "AI civilization" literature reports rich emergent phenomena in simulated societies of LLM agents: conventions, economies, governments. Two questions follow for practitioners. **What in an agent's instructions changes its social behavior?** And **which of the lessons from multi-agent simulations transfer to getting better results from agents in ordinary work?**

Game theory offers a mature vocabulary and a set of minimal, well-understood environments for these questions. The Prisoner's Dilemma isolates the tension between individual and collective payoff. A Bertrand duopoly isolates tacit collusion. Invasion and replicator analyses separate *behaving* cooperatively from being *evolutionarily stable*. Image-scoring reputation (Nowak & Sigmund, 1998) gives a canonical mechanism for cooperation among strangers. Because the environments are simple, the effect of a single sentence in a system prompt can be measured against a control with little ambiguity.

This paper reports a compact, low-budget program that uses these instruments on one production model, Claude Haiku 4.5. It extracts lessons at two levels: what practitioners should do when instructing agents, and what researchers should do when running such studies. Our contributions are:

- **A keyword-sensitivity map for collusion and defection.** We identify a specific, innocuous-looking phrase that reliably induces tacit price collusion, and two phrases that trigger immediate defection. We also show that prosocial phrasing has no measurable effect above a good baseline, which is an asymmetry with direct implications for prompt review.
- **A full reputation arc on LLM agents.** The arc runs from anonymous invasion, through lifetime reputation and a trust-then-betray exploit, to a recency-weighted repair, and finally a stress test under noise and forgery. The (in)stability claims are confirmed with an explicit replicator dynamic rather than asserted from payoff snapshots.
- **A construct-valid transfer demo.** Rebuilt after an internal review exposed a chain-of-thought ablation mislabeled as "urgency", the demo isolates reasoning as the operative lever and shows that personas, verification and naive fan-out are redundant once reasoning is allowed.
- **An honest methods record.** We document the failure modes we hit (a silent model fallback, unbounded extended thinking, salted-hash seeding, pseudo-replicated confidence intervals, a mechanical tipping artifact) and how we detected them. Budget-constrained LLM social-science work is likely to hit the same failures.

---

## 2. Related work

**LLM agents in repeated games.** Akata et al. (2023/2025) found that GPT-4 plays the iterated Prisoner's Dilemma unforgivingly and struggles with coordination games. Fontana et al. (2024) reported LLMs "nicer than humans" in the IPD. Several 2025–2026 studies report that explicit reasoning can erode cooperation ("Corrupted by Reasoning" [verify]), and that model identity predicts collective outcomes more strongly than prompt or game. Our strategy-panel results (nice, provocable, non-exploiting) are consistent with the "nicer than humans" profile. Our GovSim thinking contrast runs in the *opposite* direction to "reasoning erodes cooperation" in a commons setting, a tension we note but cannot resolve with n = 1.

**Collusion.** Fish, Gonczarowski and Shorrer (2024) showed that LLM pricing agents collude tacitly, and that seemingly innocuous prompt variations shift the degree of collusion. Later work reports collusion that is easy to elicit and easy to break [verify: "Fragility of Agent Collusion", 2026]. Our pricing result provides a minimal, single-sentence instance with a validated control and anti-collusion arms.

**Commons and institutions.** GovSim (Piatti et al., 2024) found that most LLM populations over-harvest a shared resource, and that "universalization" prompting improves sustainability. Our commons variant adds optional, uninstructed enforcement. It replicates the universalization benefit, weakly, and finds enforcement used only retaliatorily.

**Conventions and collective bias.** Ashery, Aiello and Baronchelli (2025) showed spontaneous convention formation, collective bias and committed-minority tipping in LLM populations. We replicate convention formation and collective bias on a model family they did not test. Our tipping result is inconclusive.

**Reputation and indirect reciprocity.** Nowak and Sigmund (1998) introduced image scoring. Later theory established that reputation dynamics depend on assessment rules, observation errors and private versus public information. Recent LLM work examines reputation-based cooperation among agents [verify: arXiv 2608.04507]. We contribute an adversarial sequence (trust-then-betray, recency, noise, forgery) run end to end on LLM agents.

**Prompting levers and multi-agent orchestration.** Evidence on emotional prompts (Li et al., 2023), personas (Zheng et al., 2024), and tips and threats (Meincke, Mollick et al., 2025 "Prompting Science Reports") suggests small, inconsistent effects at scale. Chain-of-thought (Wei et al., 2022) and self-consistency voting (Wang et al., 2023) are established accuracy levers. Critiques of multi-agent debate (Du et al., 2023, and follow-ups) and failure taxonomies for multi-agent systems (Cemri et al., 2025) motivate our fair-fan-out comparison. Validity critiques of LLM social simulation (the PIMMUR principles [verify]) shaped our design.

---

## 3. Testbed and methods

### 3.1 Harness

All model calls go through one module that caches every call in an append-only store keyed by a hash of (model family, system prompt, user prompt, key). This makes every run resumable and every number traceable to a stored response. Each call logs the served model id, token counts, cost and latency. A **strict model-family guard** rejects and retries any response served by a different model family than requested. We added it after discovering that requests for a larger model were silently served by Haiku about half the time. Game logic is kept in pure modules with no model calls.

### 3.2 Model and settings

The model is Claude Haiku 4.5 via the Claude Agent SDK, with SDK-default sampling. Extended thinking was **disabled** (`thinking: disabled`) except in one labeled contrast. With thinking enabled, the model emitted thousands of thinking tokens (up to about 10,000 logged) for single-number decisions, and token caps were not honored.

### 3.3 Design principles

- **One varied sentence** per condition, with everything else identical.
- **A control arm plus wrong-direction probe arms**, which validate that the measure can move both ways.
- **Hypothesis-blind prompts** that describe payoffs only.
- **Forced machine-readable output** (`MOVE: C`, `ANSWER: n`). The parse fallback rate was audited on the first nine experiments and was 0% across 5,568 parsed outputs.
- **Several seeds**, with seeded random pairing.

### 3.4 Environments

| Environment | Agents | Horizon | Key manipulation |
|---|---|---|---|
| Pricing duopoly (cost 10, demand 30 − p_min, prices 10–30) | 2 | 15 rounds | 9 one-sentence interventions |
| Iterated PD (T5/R3/P1/S0) | 2 | 15 rounds | 8 one-sentence interventions |
| Strategy panel | Haiku vs AllC/AllD/TFT/GRIM/Random | 15 rounds | opponent |
| Group PD, anonymous | 7 Haiku + 1 AllD | 12 rounds, random re-pairing | invader present or absent |
| Group PD + reputation | same | 12 rounds | partner's lifetime cooperation rate shown |
| Stealth invader | same | 12 rounds | invader cooperates through round K ∈ {3,6,9}, then defects |
| Recency reputation | same | 12 rounds | last-3 window, or one-strike (defected in last 2) |
| Noisy / forged reputation | same | 12 rounds, K=6 | flip prob. ε ∈ {0,.15,.3,.5}; forged all-C window |
| Replicator dynamics | 8 (C or D strategies) | 8 gens × 2 rounds | anonymous vs reputation; initial D ∈ {1,3} |
| Naming game | 24 | 24 rounds (+8 minority) | committed minority 5–35% |
| Commons ("GovSim with teeth") | 5 | 12 months | none / fines / fines+exclusion / +universalization; thinking on |
| Transfer demo | 1 (or 3 voters) | 24 items × 4 repeats | reasoning × {plain, persona, vote} + verify |

### 3.5 Measures and statistics

- **Collusion index:** (back-half mean price − 10) / 10, where 1.0 is the joint-monopoly price of 20.
- **Cooperation and first-defection round.**
- **Invasion fitness:** invader payoff minus mean resident payoff.
- **Defector fraction** across generations.
- **Accuracy** on problems with computed ground truth.

CIs are percentile bootstraps over clusters (seeds or problems, 5,000 resamples). Tests are cluster-level permutation tests, with Holm–Bonferroni correction within each keyword sweep.

---

## 4. Results

### 4.1 One sentence switches collusion on

Under the neutral prompt, two Haiku sellers priced near the competitive level (collusion index 0.243, 8 seeds). Appending *"Avoid destructive price wars with the other seller; they hurt everyone's profits"* produced an index of **0.962**. In seven of eight pairs, both firms locked onto exactly 20, the joint-monopoly price, with no communication channel (permutation p ≈ 0.0002, the test's floor; survives Holm). "Think carefully about your long-run profits" raised the mean to 0.414, but only because one seed reached full collusion (p = 0.098, n.s.). Six anti-collusion phrasings, which name antitrust, regulators, rivalry, consumers or aggressive competition, produced indices of 0.18–0.25, indistinguishable from control.

![Figure 1. Collusion index by pricing phrase (left) and IPD cooperation by phrase (right).](figs/collusion_defection.png)

### 4.2 One sentence switches defection on; prosocial sentences do nothing

In the 15-round IPD, Haiku cooperated in **every round of every game** under the neutral prompt and under five prosocial phrasings: reputation, retaliation, universalization, first-mover and golden rule. *"Protect your own score above all else, and do not trust the other player"* dropped cooperation to **0.10**, and *"Only the current round matters to you; assume there is no future"* dropped it to **0.05**. The first defection came on round 1 in 8 of 10 games (both p ≈ 0.007, Holm-corrected).

### 4.3 The disposition: an Axelrod cooperator, not a maximizer

Against fixed strategies, Haiku cooperated in round 1 against everyone. It sustained full cooperation with TFT and GRIM, retaliated against AllD 93% of the time, and played roughly tit-for-tat against Random (cooperation 0.51, retaliation 0.61, forgiveness 0.49). It **did not exploit AllC** (45–45) and **lost to AllD** (13–23).

![Figure 2. Strategy panel fingerprint and single-defector invasion.](figs/gametheory.png)

### 4.4 Robust behavior, unstable equilibrium

In an anonymous 8-agent population, a single always-defector barely changed group cooperation (0.995 → 0.938). However, it earned **58** against the residents' **30**, giving invasion fitness +27.8 (range +26.0 to +29.7 over 4 seeds). An explicit copy-the-richer replicator dynamic confirms that this payoff advantage drives selection. Under anonymity, the defector share rose from 1/8 to a mean of **0.54** and from 3/8 to **0.75**, in all six runs. With partner reputation visible, it fell to **0.04** and **0.21** respectively, reaching all-cooperator fixation in 2 of 3 runs from 1/8.

![Figure 3. Replicator dynamics: defector share by generation, anonymous vs reputation.](figs/replicator.png)

### 4.5 Reputation: loud cheaters, patient cheaters, noise and forgery

Showing each agent its partner's lifetime cooperation rate turned the naive defector's invasion fitness from +27.8 to **−16.3**. Residents cooperated with each other 99% of the time but with the known defector only 8%, without being told to do so.

A **trust-then-betray** invader that cooperates for K rounds before defecting invaded profitably at every timing: **+10.4, +13.6 and +7.3** for betrayal from rounds 4, 7 and 10. It still received 69–100% cooperation after betraying, because a lifetime average barely moves after a few late defections.

Replacing the lifetime score with a **3-round recency window** cut the mid-game exploit to **+0.8**, and early betrayal to **−4.0**. A **one-strike** signal gave −2.8 and −1.2. Only last-phase betrayal remained mildly profitable (+4 to +6), which is the standard end-game effect in finitely repeated games.

Under **symmetric observation noise** that flips each observed move with probability up to 0.5, the exploit stayed shut (fitness −2.0 to +3.3). Residents' payoffs fell from 33.9 to 26.7 because honest cooperators were misjudged. When the invader could **forge** a clean recent record, fitness returned to **+14.6**. The betrayer received 100% cooperation after betraying and earned 48, the highest mean payoff of any trust-then-betray condition.

![Figure 4. Stealth invasion fitness under lifetime, window and one-strike reputation.](figs/recency.png)

![Figure 5. Recency reputation under observation noise and forgery.](figs/noisy.png)

### 4.6 Transfer: reasoning is the lever; personas, verification and voting are redundant

On 24 multi-step word problems (selected for a mid-difficulty band; disclosed), with 96 attempts per condition, the results were:

- **Answer-only prompting:** 60.4% accuracy (95% cluster CI 43–77%).
- **"Show brief working":** **100%**.
- **A verification pass:** 99%.
- **An expert persona:** 68% without reasoning and 99% with it.
- **A three-agent majority vote:** 64% over answer-only samples and 99% over reasoning samples, at three times the cost.

Reasoning separates the two families cleanly. Nothing else does.

![Figure 6. Transfer demo v2: accuracy by condition with problem-clustered 95% CIs.](figs/practical2.png)

### 4.7 Deliberation and the commons; conventions without institutions

Five agents sharing a regenerating lake collapsed it in every thinking-off run without enforcement (0/3), and every run with fines (0/3). Fines were never used when they were the only tool. With exclusion also available (0/3), fines were used 5–13 times per run, always after over-harvesting had already occurred. Adding a universalization cue ("consider what would happen if everyone in your position did the same") produced the only surviving thinking-off run (1/3): 560 tons caught over 12 months, 5.6× the collapse haul, with 22 fines and one exclusion. The single thinking-on run of the no-enforcement condition also survived (total catch 240).

In a 24-agent naming game, all three seeds formed a convention by round 10–11 and **all chose the same name**. That name was already chosen by 42–50% of agents in round 1, against 10% expected by chance: strong collective bias. Committed minorities of up to 35% did not tip the convention within 8 rounds. After removing the mechanical contribution of the committed agents themselves, conversions of non-committed agents were transient at 15–25% (at most 3 of 18). At 35%, 2 of 16 switched and stayed switched through round 8.

![Figure 7. Naming game: convention formation (left) and genuine conversion of non-committed agents under a committed minority (right).](figs/tipping_corrected.png)

---

## 5. Applied lessons

We translate the results into rules for people who deploy agents. Each rule is scoped to what we measured.

**L1. Review agent instructions for *harmful* phrases, not for missing *helpful* ones.** Risk is asymmetric. A good default cooperator or competitor cannot be made measurably better with more prosocial language, but one sentence can switch on collusion or defection. The dangerous phrases look reasonable in isolation: "avoid price wars" sounds like prudent business advice, and "protect your own score, don't trust the other party" sounds like sensible negotiation hygiene. *Practice:* add a prompt-review checklist for agents in competitive or cooperative settings. Flag language about avoiding conflict with competitors, distrust of counterparties, and short-horizon framing ("only this deal matters"). Test system prompts against a control before deployment, as one would test code.

**L2. Pricing and bidding agents can collude tacitly without any channel. Audit outcomes, not messages.** The agents in 4.1 never communicated. They reached the monopoly price through framing alone. Monitoring that looks for explicit coordination would miss this entirely. *Practice:* monitor realized prices or bids against competitive benchmarks, and treat "avoid price war" style objectives as a compliance risk.

**L3. A well-behaved agent population is not a safe one. Plan for the exploiter.** Cooperative agents keep cooperating in the presence of a free-rider, which is exactly what makes the free-rider profitable. In any system where agents choose whom to work with (marketplaces, agent-to-agent APIs, delegation networks), a small number of defecting agents can capture a large share of value, and under imitation or selection pressure their strategy spreads. *Practice:* do not infer system robustness from average behavior. Measure the payoff *advantage* of a deviant agent.

**L4. If you use reputation, make it recent, and make it tamper-evident.** Our reputation results give a concrete design recipe:

- **Honest reputation disarms obvious bad actors.**
- **Lifetime averages invite trust-then-betray.** An agent can build a clean record and cash it in.
- **Weight recent behavior heavily.** A short window or a one-strike flag closes that exploit.
- **Accept that noise has a welfare cost.** It does not create an exploit, but a noisy reputation lowers everyone's payoff.
- **Never let agents self-report reputation.** Forgery defeats everything. *Practice:* compute agent trust scores in the environment, from logged behavior, with recency weighting. Treat any self-asserted or agent-supplied history as untrusted. Expect end-of-horizon defection and design explicit final-round safeguards (escrow, delayed settlement).

**L5. Let the agent reason before you add anything else.** On a task with headroom, permission to show working moved accuracy from 60% to 100%. Once reasoning was allowed, every other popular lever (an expert persona, a self-verification step, a three-agent vote) added nothing measurable, and the vote cost three times as much. *Practice:* the first fix for a wrong answer is to remove "answer only / be brief / no explanation" constraints on non-trivial tasks. Try personas and multi-agent fan-out only after that, and measure them against a single reasoning call at equal cost.

**L6. Multi-agent fan-out cannot recover what each agent lacks.** Majority voting over three answer-only samples scored no better than one (64% vs 60%). The samples were not identical, but voting cannot supply reasoning that none of the voters did. *Practice:* spend compute on deliberation within an agent before spending it on more agents.

**L7. Deliberation, or a universalization cue, changes collective outcomes more than tools do.** Agents handed fines and exclusion votes, with no instruction to use them, used them only after harm had occurred and still exhausted the commons. A single "what if everyone did this?" sentence, or enabling extended thinking, were the only interventions associated with survival. *Practice:* when agents share a resource (API quotas, budgets, compute), give them explicit collective-consequence framing or deliberation time. Do not assume that available governance tools will be used preventively.

**Methodological lessons for budget LLM social science.**

- **M-a. Verify the served model on every call.** Silent fallbacks can contaminate an entire arm (223/224 calls in our case) without any error.
- **M-b. Treat reasoning settings as an experimental factor, not a cost knob.** Disabling extended thinking changed a headline commons result.
- **M-c. Cluster your uncertainty.** Repeats of the same item or seed are not independent. Naive CIs in our first demo were about 2× too narrow.
- **M-d. Check for mechanical artifacts before interpreting population metrics.** Our committed-minority "erosion" was the committed agents' own share. Always compute the effect on the *non-manipulated* agents.
- **M-e. Beware construct drift in practical demos.** Our "rushed" arm was really a chain-of-thought ablation, and our vote baseline was stacked. An adversarial internal review using separate reviewer agents, with every claim checked against code, caught what the authors missed.

---

## 6. Limitations

- **Single model.** Every result is Claude Haiku 4.5, and nearly all were run with extended thinking disabled. A Sonnet 4.6 replication was attempted but blocked by rationing on the subscription used. We make no claims about "LLMs" in general. The literature suggests model identity strongly shapes collective outcomes.
- **Small scale and short horizons.** Games ran for 8–24 rounds, populations had 2–24 agents, and there were 3–8 seeds. The literature places many interesting failures (drift, fabricated shared history) beyond about 70 turns.
- **Ceilings.** Cooperation was 1.00 in many cells, which limits the detectable effect of prosocial interventions and makes some seeds uninformative. In several reputation cells, seeds were identical.
- **Scripted invaders.** The defectors were fixed strategies, not adaptive or learning agents. The replicator used one update rule and short generations.
- **Transfer demo scope.** It is one arithmetic suite, with items selected for mid-difficulty, so the size of the reasoning gap reflects that selection. An earlier coding-task study was ceilinged and is withdrawn.
- **Thinking contrast.** It is n = 1 per cell, because thinking-on calls throttled to about 2 per minute.
- **Commons and tipping** results rest on 3 seeds and on a single seed respectively.

---

## 7. Future work

1. Cross-model replication: Sonnet, Opus and at least one non-Anthropic family, plus legacy Haiku versions to test for generational drift in the cooperation disposition.
2. A powered thinking-on/off factorial across the commons and PD lines, to test the "reasoning erodes cooperation" hypothesis directly.
3. Learning and LLM-driven invaders, multiple replicator update rules, and larger populations.
4. Partial observability, asymmetric noise, and *partial* forgery in reputation.
5. Longer horizons (50–100+ rounds), and escaping ceilings via higher temptation payoffs.
6. Transfer studies on real workloads with headroom: code, data analysis, and multi-step tool use.
7. The matched-token "one agent vs a team" experiment (harness already written).

---

## 8. Reproducibility

Code, prompts, per-seed results and figures are public (`github.com/ApriCuz54/agent-civ-lab`, MIT license). Every experiment resumes from cache. The full study costs about $37 in API-equivalent terms, and the core keyword and reputation results cost about $1–4 each. A chronological lab record with every setup, prompt, number and correction accompanies this draft.

---

## References (draft; verify all before submission)

- Akata, E., Schulz, L., Coda-Forno, J., Oh, S. J., Bethge, M., & Schulz, E. (2023/2025). Playing repeated games with large language models. arXiv:2305.16867; *Nature Human Behaviour*.
- Ashery, A. F., Aiello, L. M., & Baronchelli, A. (2025). Emergent social conventions and collective bias in LLM populations. *Science Advances*.
- Axelrod, R. (1984). *The Evolution of Cooperation*. Basic Books.
- Cemri, M., et al. (2025). Why do multi-agent LLM systems fail? arXiv:2503.13657.
- Centola, D., Becker, J., Brackbill, D., & Baronchelli, A. (2018). Experimental evidence for tipping points in social convention. *Science*, 360(6393).
- Du, Y., Li, S., Torralba, A., Tenenbaum, J. B., & Mordatch, I. (2023). Improving factuality and reasoning in language models through multiagent debate. arXiv:2305.14325.
- Fish, S., Gonczarowski, Y. A., & Shorrer, R. I. (2024). Algorithmic collusion by large language models. arXiv:2404.00806.
- Fontana, N., Pierri, F., & Aiello, L. M. (2024). Nicer than humans: How do large language models behave in the Prisoner's Dilemma? arXiv:2406.13605.
- Hammond, L., et al. (2025). Multi-agent risks from advanced AI. arXiv:2502.14143.
- Hardin, G. (1968). The tragedy of the commons. *Science*, 162(3859).
- Li, C., et al. (2023). Large language models understand and can be enhanced by emotional stimuli (EmotionPrompt). arXiv:2307.11760.
- Meincke, L., Mollick, E., Mollick, L., & Shapiro, D. (2025). Prompting Science Reports. arXiv:2503.04818 / 2508.00614 [verify].
- Nowak, M. A., & Sigmund, K. (1998). Evolution of indirect reciprocity by image scoring. *Nature*, 393.
- Ostrom, E. (1990). *Governing the Commons*. Cambridge University Press.
- Piatti, G., Jin, Z., Kleiman-Weiner, M., Schölkopf, B., Sachan, M., & Mihalcea, R. (2024). Cooperate or collapse: Emergence of sustainable cooperation in a society of LLM agents (GovSim). NeurIPS. arXiv:2404.16698.
- Vallinder, A., & Hughes, E. (2024). Cultural evolution of cooperation among LLM agents. arXiv:2412.10270.
- Wang, X., et al. (2023). Self-consistency improves chain of thought reasoning in language models. ICLR.
- Wei, J., et al. (2022). Chain-of-thought prompting elicits reasoning in large language models. NeurIPS.
- Zheng, M., Pei, J., & Jurgens, D. (2024). Is "a helpful assistant" the best role for large language models? (personas). arXiv:2311.10054.
- [verify] Corrupted by Reasoning (2025), arXiv:2506.23276. Reputation-based cooperation among LLM agents (2026), arXiv:2608.04507. Fragility of agent collusion (2026), arXiv:2603.20281. PIMMUR validity principles (2025), arXiv:2509.18052.

---

## Appendix: key tables

**Table A1. Pricing (8 seeds).** avoid_pricewar 0.962 · longrun 0.414 · regulator 0.245 · control 0.243 · antitrust 0.233 · maximize_self 0.232 · consumers 0.229 · rival 0.221 · compete 0.182.

**Table A2. IPD (5 seeds).**

- control and 5 prosocial arms: 1.000 (never defect);
- selfish: 0.100 (first defection round 1.2);
- oneshot: 0.047 (1.2).

**Table A3. Reputation arc (invasion fitness).**

- anonymous naive AllD: +27.8;
- lifetime reputation: −16.3;
- stealth K = 3 / 6 / 9: +10.4 / +13.6 / +7.3;
- window K = 3 / 6 / 9: −4.0 / +0.8 / +5.9;
- one-strike: −1.2 / −2.8 / +4.3;
- noise ε = 0 / .15 / .3 / .5: −0.6 / −1.4 / +3.3 / −2.0;
- forged: +14.6.

**Table A4. Replicator (end defector share).**

- anon: 0.125 → 0.542, and 0.375 → 0.750;
- reputation: 0.125 → 0.042, and 0.375 → 0.208.

**Table A5. Transfer demo v2 (accuracy).** noreason 0.604 · persona_noreason 0.677 · vote3_noreason 0.635 · reason 1.000 · verify 0.990 · persona_reason 0.990 · vote3_reason 0.990.
