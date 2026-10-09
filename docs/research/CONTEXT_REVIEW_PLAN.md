# Context before direction: a parallel research plan

**Prepared 8 October 2026. Owner: Aditya. Status: Ready for a literature-review execution request.**

**Purpose:** Understand what our existing numbers mean in relation to prior experiments, behavioral theory, agent benchmarks, and evaluation practice before deciding where to take Agent Civ Lab. The review must remain open to a better explanation than the current reliability framing and to the possibility that some results add little new knowledge.

**Authoritative execution copy:** `C:\Users\adich\OneDrive\Documents\Repos\agent-civ-lab\docs\research\CONTEXT_REVIEW_PLAN.md`.

This request authorizes the planning work and multiple planning scouts. Three scouts have helped design this plan and checked primary starting points. It does **not** mean the full review below has been completed. The next stage is literature and existing-data interpretation, not new model experiments or a predetermined mitigation project.

## 1. What we need to learn

The review should answer six questions:

1. **Precedent:** Which findings reproduce known effects, contradict prior results, or differ too much to compare?
2. **Mechanism:** Which explanations are actually identified by experiments, and which merely fit the observations?
3. **Conditions:** Which incentives, information displays, interaction structures, budgets, and model configurations explain apparent disagreement between studies?
4. **Measurement:** What population, behavior, and uncertainty do our metrics really describe?
5. **Importance:** Would a clearer result change how someone evaluates, selects, or deploys agents, or contribute to a meaningful scientific question?
6. **Direction:** After the evidence is assembled, which project options are defensible, feasible, and worth pursuing—and which should be dropped?

The review is a structured scoping and evidence-mapping exercise. It must not call itself an exhaustive systematic review or meta-analysis unless its coverage and methods justify those terms.

## 2. Start from the evidence we actually have

The coordinator creates a frozen result-to-design register using the current technical report, generated evidence audit, preregistrations, scoring code, and raw-data paths. This is an inventory, not a new statistical analysis.

| Evidence anchor | Question the literature must help answer | Interpretations to challenge |
|---|---|---|
| T2: adding worker confidence assertions reduces post-change accuracy | How do selectors combine checked performance, asserted confidence, and source cues? | Authority language, numeric confidence, information overload, presentation effects, or ordinary response to an imposed distribution shift |
| T2: recent history has a modest uncertain improvement | When should a short window outperform lifetime history? | Better change-point tracking versus recency attention, reduced arithmetic burden, or a small-sample artifact |
| T5: selected phrases reduce policy accuracy; individual phrases differ | Which instructions create an operationally important conflict? | Authorized discretion, customer appeasement, hierarchy failure, repeated pressure, or task-specific scoring |
| Pricing: wording susceptibility in much of the roster | What is known about price-war aversion and supracompetitive pricing? | Replication versus extension; strategic response versus semantic instruction; index inflation versus economically useful collusion |
| Reputation games: recent signals reduce stealth payoffs; forgery raises them | What assumptions make reputation useful, and what breaks it? | Scripted change point, identity persistence, truthful observations, costless forgery, finite-horizon effects |
| PD and strategy profiles vary across models | Is behavior a stable trait or a policy induced by task representation? | Payoff maximization, preference training, language framing, opponent adaptation, inference configuration |
| T3: universalization and placebo at a survival floor; calculated-share transparency has successes | What enables sustainable resource use? | State information, arithmetic assistance, observability, communication, enforcement, or environment severity |
| Phase C: stated equal-share benchmark and requests disagree | What can verbal estimates tell us about understanding and action? | Inaccurate estimates, strategic allocation, unclear fairness rules, incentives, depleted-state artifacts—not assumed intent |
| T4: mixed ensembles do not establish a gain under the chosen matching procedure | When does diversity help? | Error covariance, shared training, sample quality, selection leakage, aggregation rule, and task difficulty |
| T4b: answer-only configuration performs worse | How does inference allocation affect outcomes? | Output allowance, visible working, hidden reasoning, truncation, invalid-format selection—not isolated deliberation |
| Naming: convergence and preference effects | What evidence is needed to call something emergent or cultural? | Initial lexical/position priors, reinforcement dynamics, researcher-imposed minority behavior |
| Game-to-task prediction does not meet the qualifying criterion | Are game fingerprints useful diagnostics? | Weak construct alignment, low model-level power, shared family dependence, restricted ranges, or a genuinely weak connection |

Do not silently upgrade an estimate into a mechanism, treat a failed significance threshold as equivalence, or infer that an agent understands a rule because it can repeat a formula.

The corrected A/B inventory is 6,996 primary-configuration cells plus 24 temperature-robustness cells, or 7,020 completed cells. These are not independent datasets or API calls. Twelve primary configurations carry seven family labels. The separate commons addendum remains incomplete and must retain that status.

## 3. Reuse the Vault, but recheck consequential claims

The earlier Vault review contains substantial material on games, conventions, social simulation, and multi-agent systems. Reuse it as a discovery index; do not reread the entire Vault or assume a note marked `verified` establishes every interpretation in it.

Each specialist receives only the relevant paper-note names and neutral task descriptions. They must:

- Identify which sources are already covered and which areas are missing or outdated.
- Deduplicate paper versions and companion notes before counting coverage.
- Reopen the primary source for every claim material to the final synthesis.
- Check whether the note's interpretation is stronger than the paper's measurement.
- Search forward from older papers through the review cutoff, while retaining foundational theory.
- Preserve historical notes and raw reports. Proposed corrections go in a new correction register first.

Examples of statements to test rather than inherit: “reasoning strips away niceness,” “generosity and exploitability are the same trait,” “diversity beats replication,” and “institutions do not emerge.” Those may summarize a specific setup, not general agent behavior.

## 4. Team architecture

Use **one coordinator, nine specialist assignments, one novelty/integration assignment, two synthesis roles, and an independent source-verification assignment**. These are jobs, not simultaneous processes.

The available capacity is four active agents including the coordinator, so run **three workers at a time**. Keep workers in separate contexts and separate output directories. The coordinator owns the shared register, deduplication, dependencies, and final synthesis; specialists never concurrently edit a shared ledger.

### Specialist assignments

| ID | Assignment | Main ownership | Questions that could change our interpretation |
|---|---|---|---|
| R1 | Evidence, confidence, and reliance | Worker assertions; calibration; source credibility; automation/advice-taking theory | Does “verified” differ from confidence? Are agents evaluating evidence, recognizing authority, or coping with complexity? |
| R2 | Instructions, objectives, and authority | Policy conflicts; instruction priority; discretion; sycophancy; indirect injection | Is an apparent violation ordinary compliance with conflicting authorized goals, or a failure across a trust boundary? |
| R3 | Repeated games and reputation | Reciprocity; PD; invasion; reputation noise, recency, forgery; evolutionary dynamics | Which equilibrium/learning assumptions are actually present? Does the repair remove invasion advantage or merely reduce it? |
| R4 | Commons, fairness, and institutions | Resource dynamics; sustainability; information; communication; sanctions; institutional design | Is failure caused by incentives, comprehension, missing coordination powers, or a severe environment? |
| R5 | Markets, negotiation, and objective specification | Pricing; bargaining; outside options; deadlines; profit versus welfare | Are pricing and buyer negotiation structurally comparable? When does an individually successful action harm the group? |
| R6 | Emergence, conventions, and behavioral persistence | Naming priors; conformity; cultural transmission; memory/drift; heterogeneity | Which population outcomes require interaction rather than shared priors or simple scripted updates? |
| R7 | Ensembles and agent-system coordination | Error covariance; voting; debate; topology; role specialization; compute matching | What does model diversity add after controlling sample quality and resource use? |
| R8 | Reasoning, training, and inference configuration | Visible working; hidden reasoning; effort; token allocation; model-family/generation differences | Which observed differences belong to reasoning, capacity, instruction tuning, truncation, or hosting? |
| R9 | Validity, statistics, and benchmark design | Estimands; dependence; nulls; holdouts; ecological validity; selection; uncertainty | What can our fixed roster and small task sets support, and which comparisons are not identified? |
| R10 | Closest precedents and contribution map | Integrate the nearest work from R1–R9; overlap; replication; artifacts; feasibility | What contribution remains once closely related papers and methodological limitations are accounted for? |

Overlap is intentional at boundaries, but one owner extracts a paper in depth. A second agent links to that extraction and independently verifies the relevant claim. Shared experiments or author groups are not independent replications merely because different specialists cite them.

### Initial execution waves

| Wave | Three active jobs | Coordinator work |
|---|---|---|
| 0 | Existing-design inventory; prior-note index; neutral task-packet preparation | Freeze search protocol, output schema, and outcome-withholding rules |
| 1 | R1 evidence/reliance; R3 repeated games; R9 methods | Merge candidate sources; identify missing constructs and broken comparisons |
| 2 | R2 instruction conflicts; R4 commons; R7 ensembles | Route overlap; screen novelty claims; maintain contrary-evidence coverage |
| 3 | R5 markets; R6 emergence; R8 reasoning | Complete result coverage and cross-domain boundary notes |
| 4 | R10 nearest-work map; constructive synthesis; independent rival-explanation synthesis | Give all three the frozen merged ledger; keep their first interpretations separate |
| 4b | Follow-ups to the same three roles after their first outputs arrive | Cross-examine the proposed narratives and nearest-work map; record disagreements |
| 5 | Independent source verification; targeted gap search; independent reconciliation check | Produce corrected interpretation register and decision dossier |

Waves are a default schedule, not a fixed dependency wall. Start a ready packet when a slot opens. Do not launch nine workers despite the concurrency limit. Do not use new user-owned chats as a substitute for subagents.

## 5. Specialist questions and boundaries

### R1 — evidence, confidence, and reliance

Review confidence calibration versus confidence presentation; self-assessment versus judging another agent; human automation misuse/disuse; advice-taking and credibility; nonstationary worker reliability; verification cost and abstention.

Compare no confidence, calibrated confidence, misleading confidence, asserted verification, and authenticated checked records. Ask whether accuracy displays contain counts or percentages, which history is visible, whether independent checking is possible, and whether worker identities are randomized.

Our worker task imposes deterioration in a scripted worker. Do not describe that as an LLM's strategic betrayal without evidence. A shorter window changes variance and information volume as well as recency.

Initial searches: `LLM advice taking confidence authority`; `agent worker selection nonstationary reliability`; `verbalized confidence calibration distribution shift`; `automation bias source reliability`; `trust calibration monitoring automation`.

### R2 — instructions, objectives, and authority

Review same-priority objective conflict, instruction hierarchy, tool/user trust boundaries, policy adherence, legitimate delegated exceptions, sycophancy, persuasion, and customer pressure. Include benchmarks with ordinary task failures, not only successful attacks.

Separate commands from factual claims; helpfulness from satisfaction maximization; tone from discretion; an explicit exception power from an unauthorized exception; low-priority injection from a conflicting system instruction. Determine whether the model is scored against the same objective it was actually given.

Initial searches: `instruction hierarchy conflict policy adherence`; `LLM conflicting objectives discretion customer support`; `sycophancy truthful response user pressure`; `agent indirect prompt injection benign utility`; `refund policy benchmark tool agent user`.

### R3 — repeated games and reputation

Review fixed versus indefinite horizons, partner persistence, payoff matrices, noisy observations, indirect reciprocity, second-order norms, reputation manipulation, identity reset, change-point detection, and evolutionary imitation.

Record whether policies learn through weights, prompts, memory, or no learning at all. Distinguish a finite trajectory against a specified invader from an ESS proof. Compare recency estimators under stationary and changing behavior, including false accusations and welfare costs. Treat Bayesian filtering as a possible baseline theory, not an assumed account of model cognition.

Initial searches: `LLM repeated games reputation cooperation`; `indirect reciprocity noisy reputation`; `strategic reputation manipulation trust then defect`; `nonstationary reputation change point detection`; `LLM evolutionary strategy selection`.

### R4 — commons, fairness, and institutions

Review resource models, feasible sustainable policies, harvest order, information ladders, regeneration, communication, monitoring, exclusion, sanctions, collective choice, unequal needs, and incentives for restraint.

Compare our budget transparency bundle with studies supplying only social history, only arithmetic/state information, or actual enforcement. Check whether a resource can recover after a crash and whether sustainable behavior is possible for an individual acting alone. Do not equate universalization with an institution or an equal-share threshold with a mandatory rule.

Initial searches: `LLM commons universalization communication sanctions`; `common pool resource institutional design monitoring`; `agent resource allocation transparency incentives`; `LLM fairness scarce resources`; `understanding versus action social dilemma`.

### R5 — markets, negotiation, and objective specification

Review repeated pricing, auction and bargaining studies; reservation values; outside options; deadlines; communication; memory; differentiated goods; adaptive counterpart behavior; and individual versus social objectives.

Analyze whether an elevated price index has the same interpretation in different markets. Identify economic baselines and whether a high price actually increases profit. A scripted seller interacting with a buyer is not automatically equivalent to two pricing agents sharing a market. Verify the nearest papers' actual mechanisms rather than citing agent explanations as causal evidence.

Initial searches: `LLM algorithmic collusion price war prompt`; `LLM bargaining negotiation outside option`; `language model repeated pricing differentiation`; `agent negotiation incentive compatibility`; `profit maximization welfare prompt framing`.

### R6 — emergence, conventions, and persistence

Review lexical and option-position priors, naming games, network structure, conformity, minority tipping, shared training, cultural inheritance, long-horizon memory, and drift.

Look for individual-prior controls, shuffled choices, random/scripted agents, simple reinforcement models, interaction ablations, and evidence of transmission between generations. Separate coordinated convention from rich culture or institutional emergence. Distinguish imposed commitment from spontaneously acquired norms.

Initial searches: `LLM conventions collective bias initial preference`; `naming game committed minority null model`; `LLM cultural evolution transmission`; `agent memory long horizon drift`; `multi agent conformity shared priors`.

### R7 — ensembles and coordination

Review homogeneous and heterogeneous voting, correlated errors, judge preference, communication format, topology, specialization, shared context, verifier quality, and task decomposition.

Require distinctions among equal calls, equal allowed tokens, actual tokens, latency, cost, and estimated compute. Record whether matching and evaluation share data, whether ensemble membership is selected using the test set, and whether overlapping ensembles are treated as independent. Look for both gains and failures and identify the task properties conditioning them.

Initial searches: `LLM ensemble diversity correlated errors`; `multi agent equal compute single agent`; `agent scaling coordination overhead task topology`; `multi agent debate negative results`; `test set ensemble selection bias`.

### R8 — reasoning and inference configuration

Review deliberate reasoning, visible working, hidden inference budgets, output-format constraints, truncation, reasoning effort, temperature, instruction tuning, and model/provider effects. Include rational metareasoning and bounded-rationality theory as interpretive tools.

Distinguish improving arithmetic accuracy from improving cooperation or policy adherence. Record actual allocation controls: the same weights with different effort, versus unrelated models marketed as reasoning models. Do not infer that one causes the other merely because they differ. Establish which current records could clarify a confound without new runs, and which questions require a future controlled experiment.

Initial searches: `LLM reasoning cooperation incentive`; `test time compute scaling fixed budget`; `chain of thought output tokens confound`; `reasoning model truncation instruction following`; `bounded rationality metareasoning language models`.

### R9 — methods and external validity

Map each implemented estimand and its target population. Audit model-family dependence, shared templates, paired conditions, sample exclusions, calibration pilots, conditioning on matching, floor/ceiling outcomes, missingness, and inferential calibration. Also examine selective outcome reporting, publication bias, benchmark/model availability selection, and repeated evidence across publications. Look for preregistrations, registered reports, replication attempts, and null results where discoverable; absence of accessible evidence is not evidence that no such study exists.

Review social-simulation validation as well as operational agent benchmarks. Investigate whether bootstrap sign-tail scores are justified for the current resampling structure; whether uncertainty should jointly resample shared problems and families; and whether a non-significant result can exclude a practically important effect. Separate reliability, utility, fairness, cooperation, and safety metrics.

Initial searches: `LLM agent evaluation reproducibility cost holdout`; `generative social simulation operational validity`; `hierarchical bootstrap crossed clusters models tasks`; `bootstrap hypothesis test null calibration`; `equivalence tests floor ceiling benchmark`.

### R10 — contribution mapping

After specialist extraction, identify the nearest three to five substantive precedents for each plausible contribution. Compare task, intervention, control, metric, artifact, and claim—not title similarity or arXiv recency alone.

Classify an option as known result, partial replication, scope extension, mechanism clarification, benchmark contribution, engineering artifact, or unresolved. Never turn “no paper found” into “first.” Document searched venues/terms and coverage gaps. Include the option of publishing the existing report with a narrower interpretation or ending the project.

## 6. Search and reading protocol

### Pass A — discovery without our outcome directions

Use fresh subagents with `fork_turns="none"`. Give literature specialists neutral task designs and their assigned constructs, not our effect directions, numbers, or favored article. They should first state what the literature would predict and what alternative mechanisms could operate. Freeze that memo before revealing the results.

This is limited outcome withholding, not technical blinding or independence from the chosen research topics. The coordinator and methods reviewer know the project. Fresh literature agents should not inspect result files, the report, or RUNLOG during this pass; if they need repo access, they must follow its instructions, which may expose outcomes. In that case mark the packet **outcome-aware** rather than pretending it was blind.

Search the existing note index, primary repositories (arXiv, ACL Anthology, OpenReview, publisher pages), official benchmark/code projects, and seminal theory. Use surveys to discover experiments, not as substitutes for the original experimental sources.

### Pass B — full-text extraction and citation tracing

For each consequential source, inspect methods, results, limitations, and relevant appendix/code. Trace references backward and newer citing studies forward. Search explicitly for failures, replications, alternative explanations, criticism, and corrected versions. Publication status and code availability are useful metadata, not quality certificates.

Keep a search log: query, date, source searched, candidates screened, inclusion/exclusion reason, and whether the search added an interpretation-changing mechanism or comparator. Record search-engine, language, publication, and access biases; a large accessible-preprint collection is not necessarily a representative literature sample. A source with unavailable full text remains a discovery lead; it cannot support detailed numerical or procedural claims.

### Pass C — reveal our outcomes and make structured comparisons

Provide the frozen result-to-design register after the initial literature memo. Specialists compare expected and observed behavior, including nulls, and explain which differences in design might account for agreement or disagreement.

Do not pool incompatible effect sizes. If tasks, baselines, outcome units, or budgets differ, use qualitative comparisons and state exactly why direct comparison fails. Report both favorable and unfavorable precedents.

### Coverage expectations and stopping rules

Plan for roughly 80–120 screened candidates and 40–60 unique consequential full-text sources across the program, reusing earlier work where appropriate. These are planning bands, not quotas or claims of completeness. Each specialist should initially screen approximately 10–20 candidates and extract 4–8 particularly useful sources; overlap is deduplicated.

Stop an individual search lane after backward/forward tracing and explicit contrary-evidence searches are complete, and two successive search passes add no new interpretation-changing mechanism, comparator, or material validity concern. Do not claim global saturation. Expand only a documented gap; if an important lane is sparse, record that instead of padding it.

There is no fixed wall-clock promise. Report actual coverage and blockers at each wave. Prefer deep inspection of the closest studies to collecting hundreds of abstracts.

## 7. Extraction schema and evidence standards

Every specialist uses the same structure. Store source metadata once and claim-level evidence separately.

### Source record

- Canonical ID, title, authors, year, DOI/arXiv ID, pinned version, publication status, retrieval date, primary URL, official code/data URL.
- Previous Vault note(s), if any; related versions; overlapping datasets/author groups; independence group.
- Reading status: `discovered`, `abstract_screened`, `full_text_read`, `key_claim_verified`, or `unavailable`.
- Inclusion reason, source owner, and uncertainty about identity or access.

### Claim-level record

- Claim ID and neutral research question; source ID; exact supporting page/section/table/figure or code permalink.
- Reviewer paraphrase of the observation; claimed mechanism; experimentally identified mechanism; important alternative explanation.
- Agents/population, model snapshots and families, task/environment, interaction and memory, rewards/objectives, permitted actions, and authority/trust arrangement.
- Intervention and comparator; relevant prompt paraphrase and location; task/template/seed counts and unit of randomization.
- Outcome definition and denominator, baseline, effect and unit, interval, statistical method, multiplicity family, exclusions, and holdout protocol.
- Resource accounting: calls, allowed and actual tokens, retries, verifiers/judges, hidden reasoning, latency/cost if reported.
- Support type: supportive, conflicting, null, mixed, or not comparable. Applicability: direct comparator, related mechanism, methods precedent, or background.
- Limitations; boundary conditions; implication for a particular lab claim; evidence needed to discriminate explanations.
- Independent verifier, verification status, and unresolved discrepancies.

Prefer paraphrase and source locations over copied text. Quote only short necessary excerpts, respecting source quotation limits. Do not paste whole papers, source prompts, or inaccessible summaries as though they were primary evidence.

### Comparability classification

| Class | Requirements | Permitted use |
|---|---|---|
| Direct comparator | Similar decision, information, incentive, intervention, comparator, and outcome definition | Discuss agreement/disagreement with explicit remaining differences |
| Mechanism comparator | Tests a candidate process under a different task | Support a hypothesis or boundary condition; not a numerical replication claim |
| Methods comparator | Supplies a relevant evaluation/identification principle | Diagnose validity or propose analysis requirements |
| Background analogy | Related theory or behavior with substantial mismatches | Suggest questions; cannot establish LLM psychology or a causal explanation |

Human findings belong in an explicitly labeled comparison layer. Human trust, risk aversion, and norm theories can organize hypotheses; they do not prove that language models share the same internal processes.

## 8. Outputs and file ownership

The main repo holds the evidence registry and working artifacts; the Vault holds a readable synthesis and links. No second code repo or full duplicate dataset is created.

```text
docs/research/CONTEXT_REVIEW_PLAN.md
docs/research/context_review/
  BASELINE_REGISTER.md
  SEARCH_PROTOCOL.md
  registry/sources.csv
  registry/claims.csv
  registry/search_log.csv
  workstreams/R1/... through R10/...
  verification/SOURCE_CHECKS.md
  synthesis/INTERPRETATION_MATRIX.md
  synthesis/DISAGREEMENTS.md
  synthesis/RELATED_WORK_MAP.md
  synthesis/RESEARCH_OPTIONS.md
  synthesis/DECISION_BRIEF.md
```

Each specialist writes only inside its assigned directory: `memo.md`, `sources.csv`, `claims.csv`, `search_log.csv`, and `questions_for_other_streams.md`. The coordinator merges registries deterministically and maintains canonical IDs. Verification agents own their verification directory. Source corrections are append-only findings with reasons; original preregistration and raw results remain unchanged.

A specialist memo should be approximately 1,500–2,500 words and contain:

1. What the literature establishes within its actual scope.
2. Closest comparisons and important design mismatches.
3. Competing explanations for our relevant outcomes.
4. Positive, contrary, null, and unavailable evidence.
5. The smallest information or analysis that could resolve ambiguity.
6. Cross-stream questions and priority full-text reading for the coordinator.

Avoid a string of isolated paper summaries. The registries retain the detail; the memo explains what changes our understanding.

## 9. Cross-examination and independent verification

The constructive synthesis role proposes the strongest two or three coherent explanations supported by the evidence, including the existing reliability framing and alternatives such as ecological mismatch, objective specification, or inference allocation.

The adversarial role first independently proposes rival explanations from the same frozen ledger, without waiting on another agent's unfinished synthesis. After the constructive and R10 outputs arrive, explicitly dispatch a follow-up cross-examination. It attempts to defeat each explanation with the nearest prior work, a plausible alternative, a null/boundary case, and a confound. It must also identify criticisms that are irrelevant or unsupported; negativity is not rigor by itself.

An independent source verifier checks every claim that would appear in the executive conclusion, every external numerical result used to justify a direction, and every novelty-critical comparison. It also checks a documented random sample of the remaining claim rows; the coordinator records the sampling procedure and coverage. This is source verification, not a majority vote among agents.

Resolve disagreements by returning to the source passage, environment specification, or code. Record unresolved disputes. Do not increase confidence because three agents repeat the same source or wording. Same-model agents can share errors.

## 10. What the final synthesis must contain

### A. Interpretation matrix

For every anchor in section 2, provide the current observable claim, candidate explanations, closest precedents, mismatches, what remains unidentified, and a verdict:

- **Supported within scope:** measurement and applicable evidence support the stated restricted interpretation.
- **Ambiguous:** more than one materially different explanation fits.
- **Contradicted:** a specific stronger interpretation is inconsistent with the evidence.
- **Unresolved:** insufficient accessible or comparable evidence.

These are contextual-review labels, not replacements for the original preregistered scorecard.

### B. Related-work and contribution map

Show what is already well studied, where our work is a replication, which design changes might add knowledge, and where benchmark or engineering contributions would matter more than another behavioral effect.

### C. Research-option cards

Prepare a small set of genuinely different options, not variations of a predetermined worker-trust project. Options may include a focused evidence/authority mechanism study; objective-conflict evaluation; resource-governance context; a compute/dependence-correct ensemble study; a narrower replication/technical report; or stopping further experiments.

Each card must state:

- The unanswered question and the nearest competing work.
- The contribution that would remain if the result is null.
- What current data can and cannot answer.
- The smallest discriminating next study or analysis, without executing it.
- Suitable artifact: technical report, reproducibility package, benchmark, engineering component, or potential research submission.
- Expected value, feasibility under the existing no-paid-model constraint, uncertainty, and risks of weak novelty or trivial conclusions.
- Evidence that would make us reject the option.

Use qualitative judgments with reasons rather than a fake precise numerical ranking. Publication potential is provisional until closest methods and artifacts are examined.

### D. Decision brief for Aditya

Write a readable brief of approximately 3–5 pages: what we learned, what changed from the current article, which narratives survived, which numbers are less meaningful than they appeared, and the strongest remaining options. Include a short reading list and unresolved questions.

The decision is made **after** this brief. The review may recommend an option with reasons, but no implementation or model batch follows automatically. Keep current drafts marked as drafts until source verification and any material corrections are complete.

## 11. Gates and completion criteria

| Gate | Pass condition | If it fails |
|---|---|---|
| G0: baseline integrity | Every anchor traces to implemented scoring and recorded data; study status is explicit | Resolve the discrepancy or narrow the anchor |
| G1: balanced coverage | All nine specialist areas covered; consequential sources read; contrary/null searches logged | Target the missing lane; do not generalize from abstracts |
| G2: source verification | Executive and novelty-critical claims independently checked against primary passages | Downgrade or remove unsupported claims |
| G3: interpretation | Observations separated from mechanism, intent, and generalization; disagreements recorded | Preserve ambiguity instead of forcing a single story |
| G4: contribution | Options compared with their nearest precedents and feasible discriminating work | Classify as replication/report or reject the option |
| G5: delivery | Verified decision brief, options, reading list, and explicit coverage gaps handed to Aditya | Finish the missing deliverable; do not wait indefinitely for a project choice |
| Subsequent human decision | Aditya chooses a direction, a narrower report, or no additional work | No implementation or new experiments automatically |

Done means all material existing result families have a contextual disposition, major external claims are verified, inaccessible evidence is labeled, contrary evidence is retained, and the owner can choose among concrete options. Review execution is complete at verified delivery; the owner's later project choice is a separate step. It does not mean the team found a publishable novelty claim or read every paper on agents.

## 12. Primary starting points

These are discovery seeds checked during planning at metadata/abstract level or through primary search results, unless explicitly noted. They are **not** completed full-text extractions. Existing Vault notes do not remove the need for method and claim verification. Recheck versions during execution.

| Area | Primary starting point | What to inspect |
|---|---|---|
| Human reliance | [Parasuraman and Riley: Humans and Automation](https://journals.sagepub.com/doi/10.1518/001872097778543886) | Definitions, monitoring opportunities, and experiments behind misuse/disuse categories |
| Human trust | [Lee and See: Trust in Automation](https://journals.sagepub.com/doi/10.1518/hfes.46.1.50_30392) | Conceptual framework and original evidence; full-text access remains unresolved |
| Confidence | [Language Models (Mostly) Know What They Know](https://arxiv.org/abs/2207.05221) | Self-assessment versus worker assessment; probability versus verbal confidence; domain transfer |
| Sycophancy | [Towards Understanding Sycophancy in Language Models](https://arxiv.org/abs/2310.13548) | Operational definition, training evidence, and whether it applies to policy-pressure tasks |
| Instruction priority | [The Instruction Hierarchy](https://arxiv.org/abs/2404.13208), [IHEval](https://arxiv.org/abs/2502.08745) | Trust levels, conflict generation, comparison conditions |
| External-content attacks | [InjecAgent](https://arxiv.org/abs/2403.02691), [AgentDojo](https://arxiv.org/abs/2406.13352) | Attack objectives, ordinary utility, adaptive defenses, benchmark corrections |
| Worker/tool reliance | [Agents' Overreliance on Unreliable Tools](https://arxiv.org/abs/2609.05587), [TrustFork](https://arxiv.org/abs/2609.32635) | Evidence conflicts, identity/confidence cues, actual execution effects, mitigation controls |
| Operational policy evaluation | [τ-bench](https://arxiv.org/abs/2406.12045) | Interactive tasks, policy grounding, terminal-state scoring, consistency metrics |
| Broad agent evaluation | [AgentBench](https://arxiv.org/abs/2308.03688), [AI Agents That Matter](https://arxiv.org/abs/2407.01502) | Task diversity, cost/accuracy, holdouts, reproducibility, and actual failure taxonomies |
| Repeated interaction | [Playing Repeated Games with Large Language Models](https://arxiv.org/abs/2305.16867) | Opponents, horizon, information, coordination interventions, human comparison |
| Reputation | [Emergence of Reputation-Based Cooperation in LLM Agents](https://arxiv.org/abs/2608.04507) | Donation games, strategy inheritance, selection, discrimination and invasion definitions |
| Commons | [GovSim](https://arxiv.org/abs/2404.16698) | Regeneration, communication, universalization, available enforcement, survival definitions |
| Markets | [Algorithmic Collusion by Large Language Models](https://arxiv.org/abs/2404.00806) | Market structure, memory interventions, economic metrics, causal mechanism evidence |
| Emergence | [Emergent Social Conventions and Collective Bias](https://arxiv.org/abs/2410.08948) | Initial priors, updates, interaction ablations, minority thresholds |
| Compute | [Scaling LLM Test-Time Compute Optimally](https://arxiv.org/abs/2408.03314), [Towards a Science of Scaling Agent Systems](https://arxiv.org/abs/2512.08296) | Budget definitions, task difficulty, topology, single-agent baselines |
| Simulation validity | [PIMMUR](https://arxiv.org/abs/2509.18052), [Critical Review of Generative Social Simulations](https://arxiv.org/abs/2504.03274) | Construct and operational validity, designer-imposed behavior, limits of human analogies |

Also route the existing Vault notes on correlated errors, reasoning/cooperation, fairness, memory drift, personas, and team failure to the appropriate specialists. Add classical repeated-game, institutional-design, Bayesian filtering, bargaining, and resampling references through source tracing; verify their exact formulations before applying them to our tasks.

## 13. Dispatch instructions

Use this common preamble for a specialist:

> You are specialist R_. Your job is to contextualize a defined set of agent tasks, not support a preferred narrative or choose the next project. Use primary sources, inspect methods for consequential claims, retain contrary and null evidence, distinguish observations from mechanisms, and state reading/access limits. In Pass A, do not inspect our numerical outcomes; record literature-based expectations first. Write only your assigned workstream files. Do not run models, edit raw results or preregistration, publish, contact authors, or change the existing experiment queue. Return a comparison memo, source/claim records, search log, and cross-stream questions.

Append the role's questions from section 5, relevant existing note names, neutral task packet, output schema, cutoff, and owned directory. Use a fresh context. A numerical source claim needs a exact passage locator and eventual independent verification. Escalate ambiguous overlap to the coordinator rather than editing another agent's files.

For the constructive synthesis role:

> Read the merged evidence, then propose the strongest coherent interpretations that survive it. Include alternatives to the current framing. Identify what is already known, what our work adds, and what cannot yet be inferred. Do not choose a direction before assessing the closest precedents.

For the adversarial role:

> Attempt to falsify each proposed interpretation using the strongest applicable prior work, alternative explanation, null result, and design mismatch. Also identify invalid criticisms. Do not manufacture novelty or dismiss a result merely because it is small or synthetic. Maintain a disagreement register with exact sources.

For the source verifier:

> Independently open primary sources and verify bibliographic identity, version, and the exact claim-to-passage link. Check effect units, denominators, controls, resource budgets, and whether the cited result really supports its use. Mark supported, overstated, incorrect, or unresolved. Do not treat another agent's summary as evidence.

For the coordinator:

> Preserve output ownership and the four-slot concurrency limit, merge canonical sources, enforce reading-status and comparability rules, route gaps, and adjudicate by evidence rather than agent agreement. Produce the interpretation matrix and decision dossier. Keep experiment results immutable and delay project-direction execution until the review decision.

## 14. Boundaries for this phase

The user has explicitly requested broader context before choosing a direction. This takes precedence over the older rule that all work must immediately serve the original Q0 scorecard. The original experiment design remains historical evidence; the new review may examine alternative interpretations and contributions.

The existing no-paid-model, secret-handling, result-integrity, and publication rules remain applicable. This phase needs web/library reading and existing-file inspection, not provider API calls. Offline reanalysis, new experiments, new keys, publication, and external messaging are outside the planned review unless separately authorized. Ordinary literature access and local review artifacts are within scope.

The planning scouts' initial contributions should be treated as planning input, not final literature verdicts. Their key lesson is to organize evidence around **implemented measurements, comparable precedents, and justified interpretation** rather than accumulate agreeable summaries.

[Current report](../report/technical_report.md) · [Original program plan](../v2/PROGRAM_PLAN.md) · [Run log](../../RUNLOG.md)
