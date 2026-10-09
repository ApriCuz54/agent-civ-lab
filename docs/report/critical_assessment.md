# Critical assessment: what this project is worth

**8 October 2026 · Internal assessment, not part of the public article**

## My recommendation

Lead with **LLM Agent Reliability Evaluation**, and use **When Instructions Compete** as the report title. Position the work as an independent engineering research project with controlled behavioral experiments. The strongest empirical core is the worker-assertion penalty and selected refund-policy phrase effects; the strongest portfolio core is the inspectable evaluation harness.

It is a credible supplementary project for agent evaluation, applied ML, and reliability work. It is less direct evidence for compiler, kernel, or inference-performance roles than the existing AMD work. Do not spend additional months making this broader merely to make the résumé entry sound bigger. Finish an artifact a reviewer can understand in minutes.

## What I would and would not try to publish

The current evidence can support a strong technical article and an unreviewed research report. A narrowly framed workshop-style submission could be developed, but acceptance is not something these results establish. A competitive main-conference paper is not ready on the present evidence: novelty is mixed, tasks are synthetic and small, some controls bundle mechanisms, and a few inferential assumptions need work.

The strongest narrow research question would be: **How do worker confidence assertions and policy-conflicting objectives change decisions when checked evidence or explicit rules remain visible?** The present studies support that question imperfectly. They do not isolate confidence vocabulary, numerical certainty, asserted verification, and authorized flexibility. A new held-out evaluation would be required before claiming a reusable mechanism or detector.

The existing pricing result has substantial precedent. The commons result is interesting but not ready for a headline such as “AI knowingly breaks rules.” The broad game-to-task transfer question yielded weak or null support. Rebranding every result as a success would make the project less credible.

## Strengths a reviewer can actually verify

- Twelve logged model configurations and inspectable model-level outcomes, with task-specific exclusions.
- Automatically scored environments and deterministic scripted counterparts.
- Preregistration, pilot history, failed contrasts, and documented procedural deviations.
- Resumable caches, quota handling, strict parsing, model-identity checks, and source-controlled analysis.
- Independent reconstruction of the central point estimates, plus earlier verification and host sensitivity outputs.
- Willingness to identify defects in previous interpretations instead of maintaining stronger unsupported claims.

The raw inventory contains 6,996 primary A/B cells plus 24 temperature copies, or 7,020 completed cells. The old “6,460 cells” figure covers the PC queue and excludes 560 Haiku cells. Neither count is an independent scientific sample-size claim. The current 45-test count establishes that the suite runs, not that every scientific assumption has been validated. None of the implausible smoke-test throughput fields should appear in a performance claim.

## Weaknesses I would expect in an interview or review

1. **Some harms are predictable instruction conflicts.** Telling an agent to be flexible and then penalizing exceptions may show that it follows a conflicting objective. This is operationally relevant, but not automatically novel.
2. **The confidence manipulation bundles features.** Audited evidence remains intact. The added worker notes change wording and numbers for multiple workers. Authentication or provenance is a proposed implication, not an evaluated solution.
3. **Small scenario diversity.** Twelve model configurations do not compensate for four trust streams, three budget episodes, or ten shared customer-script templates per class.
4. **Model configurations are related.** Family, provider, quantization, output budget, and reasoning mode are not controlled independent factors. A random bootstrap over model configurations is not population-wide evidence.
5. **Reasoning is confounded with output allowance.** The 28.4-point result must be described as a configuration effect. Three intrinsic reasoning models were excluded from the short-output comparison.
6. **The ensemble analysis is especially weak for general conclusions.** Matching occurs on the same problem set, eligible anchors are restricted, and mixed ensembles overlap. Five calls do not imply equal compute cost.
7. **Commons claims require restraint.** A request exceeding SAFE_TOTAL/4 is not proof of comprehension or deliberate violation. SAFE-error definitions differ between preregistration sections and implementation.
8. **The statistical threshold labels are approximate.** The reported bootstrap sign-tail scores do not replace a carefully calibrated randomization or robust inferential analysis. Keep effects and intervals visible.
9. **The article's theme is post hoc.** That is acceptable for a transparent synthesis; it is not confirmatory evidence for a newly invented theory.
10. **The supplemental study is incomplete.** Do not pool partially completed cloud models into a final conclusion or silently substitute a new completion-based sample.

## The honest résumé framing

Suggested project heading: **LLM Agent Reliability Evaluation | Python, Async APIs, Experimental Design**.

Draft bullets, conditional on Aditya being able to explain and substantiate personal ownership:

- Developed an AI-assisted evaluation harness spanning 12 LLM configurations and five synthetic task families, with resumable calls, automated scoring, strict parsing, and reproducible analysis.
- Evaluated instruction conflicts and worker-confidence claims; measured a 9.9-percentage-point accuracy loss from added self-reports and an 11.7-point policy-accuracy loss from selected customer-service phrases, with preregistered controls and bootstrap intervals.

For an engineering résumé, the first bullet is stronger and more transferable. The second needs space to avoid implying a production failure or universal effect. Do not claim “improved agents by 28%,” “prevented collusion,” “built safe AI societies,” “proved game theory does not work,” or “published a paper” while this remains a draft.

The Vault's Evidence Bank currently has no registered evidence ID for this project. These are reviewable candidate bullets, not permission to insert new claims into a master résumé. Recording an evidence ID should include the report, raw-result paths, AI-assistance disclosure, and a defensible account of personal contributions.

## Finish the portfolio package before expanding the science

The report, concise article, generated figures, evidence audit, and offline reproduction command are now the concrete package. A reader should be able to find them from the repo README and see the boundary between claims and speculation.

Before public use, check all numerical claims against the generated audit, decide whether to finish or omit the commons addendum, and answer the design questions without AI assistance. The existing ownership checkpoint remains useful: explain why the controls exist, what the bootstrap resamples, which failures the parsers catch, and which result you trust least.

If you pursue a stronger research paper later, the highest-value extension is a fresh preregistered study on held-out task templates that isolates assertion wording and conflicting objectives. Add an actual enforcement or evidence-handling mechanism only if it can be evaluated against the same failures. The current paper does not need more loosely connected games.
