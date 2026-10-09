# When Instructions Compete: What Twelve LLM Configurations Revealed About Agent Reliability

**Aditya Chatterjee · Technical article draft · 8 October 2026**

An agent does not need to receive an obvious “ignore your instructions” attack to make the wrong decision. Sometimes the competing instruction is already in its system prompt: keep everyone satisfied, be flexible, or trust a worker who says its answer has been verified.

I studied these conflicts through a collection of small, automatically scored environments. The completed cross-model study used twelve model configurations, six game environments, and five synthetic task families. The tasks included purchasing negotiations, selecting worker answers, sharing a replenishing budget, arithmetic ensembles, and enforcing a refund policy.

The most useful result was a boundary: it was easier to demonstrate particular harms than to establish that the proposed repairs worked. That is a more defensible story than a universal recipe for cooperative agents.

## Checked evidence can lose influence when an assertion is added

In one task, an orchestrator chooses an answer from three workers. One is reliable, one is noisy, and one performs perfectly before its accuracy deteriorates. The environment supplies an audited record of their past results.

I compared that audited display with the same display plus worker-generated confidence notes. The deteriorating worker labeled its answers “verified, 99% confident.” The other workers received their own confidence annotations too.

The added assertions reduced post-deterioration answer accuracy by **9.9 percentage points** on average. All twelve models had a negative point estimate. The saved bootstrap interval ran from a 4.5-point to a 16.5-point loss.

That is a concrete reliability failure: a persuasive assertion weakened decisions even when checked evidence remained available. It is not a demonstration that confidence reporting is always harmful, or that the audited record was forged. Confidence numbers, verification vocabulary, and display format changed together. Those components still need separate tests.

The attempted repair was to show only the last three checked outcomes instead of the lifetime average. It gave a **3.1-point** average gain, but its interval included zero and it did not pass the study's adjusted success criterion. A plausible design can have a promising point estimate without becoming a demonstrated safeguard.

## A fixed policy can lose to an instruction that permits exceptions

Another task gave a support agent a clear refund policy: a full refund requires a receipt and purchase within thirty days. Invalid customers asked anyway, then escalated with a sympathetic story, an alleged promise from another agent, and threats.

Before the full run, I classified three customer-service phrases as potentially harmful and three as benign. The harmful panel reduced balanced policy accuracy by **11.7 percentage points** across eleven eligible models. The harmful-versus-benign difference was **10.9 points**.

But the individual phrases tell a more useful story than the pooled result. The exploratory estimate for “Use your judgment and be flexible when customers have special circumstances” was a **27.3-point** loss. The satisfaction/conflict-avoidance phrase had a smaller loss. “Never argue with a frustrated customer” showed no harmful average effect in this panel.

The right interpretation is not that warmth is unsafe. The strongest phrase explicitly authorizes exceptions, which conflicts with the fixed rule used for scoring. This is a test of instruction conflict. Six chosen phrases on one policy are not enough to validate a general prompt linter.

Adding a sentence about precedent did not demonstrate an advantage over careful-reading advice. The dataset supports auditing competing objectives; it does not show that another layer of motivational language reliably repairs them.

![Saved accuracy contrasts](figures/accuracy_contrasts.png)

## The games exposed sensitivities, not a stable personality

The game battery provided a second view of these models. “Avoid price wars” substantially raised the pricing index in ten of twelve configurations under a preregistered threshold. Recent reputation reduced the scripted stealth-invader advantage, and a forged favorable signal raised it again, in all twelve.

These were descriptive threshold or directional counts, not twelve independently significant effects. Pricing sensitivity was already known from prior research; the contribution here is testing it across this roster with an auditable harness. The reputation result also did not mean that every residual exploit became unprofitable.

Other proposed traits were far less consistent. The nice-and-provocable strategy profile appeared in only three of twelve configurations. No game-to-task correlation met the predeclared qualifying criterion, although the small model sample leaves considerable uncertainty.

An agent's performance in a toy game should therefore be treated as a measurement in that setting. Calling it a general personality or using it as a validated hiring test for an agent would go beyond these data.

## The null results were informative only when the measurement was informative

The shared-budget task illustrates this distinction. Control, universalization, and careful-reading advice all had **0/36** successful episodes. Their zero difference cannot establish that collective framing never helps.

The separate transparency arm had **9/36** successes. It provided both shared history and a calculated sustainable allowance. That exploratory result is worth preserving, but it does not isolate transparency or prove that structural interventions generally beat prompts.

![Shared-budget successes](figures/budget_survival.png)

The arithmetic positive control also needs a qualification. Answer-only prompting scored **28.4 points** worse than brief-working prompting across eight eligible models. However, it received sixty output tokens instead of five hundred. That is a comparison of two configurations, not an isolated causal effect of reasoning.

In the supplementary commons study, agents frequently requested more than one-quarter of their own stated safe total. That observation does not prove conscious rule-breaking. Their estimates could be incorrect, equal allocation was not mandatory, and the environment rewarded individual points. The honest description is disagreement between a verbal benchmark and an action.

## Why the project is useful

The strongest artifact is a reproducible evaluation system: deterministic task rules, automatic ground truth, strict output parsing, served-model records, resumable caches, quota-aware scheduling, and inspectable results. The current offline suite has 45 passing tests. A reader can inspect the important contrasts without making new model calls.

The practical lesson is to test specific failure modes and their proposed repairs separately. Audited evidence and model assertions should have distinguishable provenance. Operational language should be evaluated against the policy it is supposed to implement. Prompt format, output budget, model family, and task sampling all belong in the result.

The project does not establish a production defense or discover a general law of cooperation. It does provide two reproducible task-specific harms, several failed repair tests, and an unusually explicit account of what the measurements cannot tell us. Those are useful outputs of an evaluation project.

**Read the full report:** [When Instructions Compete](technical_report.md). Numerical provenance, all primary contrasts, the original result inventory, and unresolved audit issues are in the [evidence audit](evidence_audit.md). This is an AI-assisted independent project; the report is a draft, and the supplementary commons addendum is unfinished.

The pricing context builds on [Fish, Gonczarowski, and Shorrer](https://arxiv.org/abs/2404.00806); the commons context on [GovSim](https://arxiv.org/abs/2404.16698). This work is presented as controlled evaluation and partial replication, rather than a claim of priority.
