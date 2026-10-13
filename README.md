# Agent Civ Lab

A saved-data study of how wording, reputation and resource constraints affect LLM-agent behavior across twelve primary model configurations. The completed Phases A/B contain **6,996 primary cells plus 24 temperature checks**. A separate Phase C addendum is incomplete.

The strongest present project is a bounded evaluation/engineering report with an auditable measurement appendix. The evidence does not yet isolate general mechanisms or establish scientific novelty. Read the [technical report](docs/report/technical_report.md), [short article](docs/report/article.md), [decision brief](docs/research/context_review/synthesis/DECISION_BRIEF.md) and [research options](docs/research/context_review/synthesis/RESEARCH_OPTIONS.md).

## Reproduce the report without API calls

Tested with **Python 3.12.10 on Windows x64**. Dependency installation needs package-network access; the reproduction command itself blocks Python socket connections and removes credential-bearing environment variables. No API key is required.

```powershell
git clone https://github.com/ApriCuz54/agent-civ-lab.git
cd agent-civ-lab
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-reproduce.txt
.\.venv\Scripts\python.exe -B -m tools.reproduce --tests
```

On macOS/Linux, use `.venv/bin/python` for the last two commands; those platforms have not yet been verified. For a second run, select a fresh destination with `--output another-output-directory`.

Outputs appear in `_reproduction/`: reconstructed audit tables/JSON, three figures, report/article HTML and `verification.json`. The verifier checks the saved v2 evidence manifest, all numerical/descriptive audit fields, valid figure files and unchanged inputs. It fails on missing/changed evidence or mismatched saved results. The copied report prose is authored text; it is not generated from scratch.

**Scope:** point estimates and descriptive inventories are recalculated. Saved confidence intervals and inferential tail scores are reused, so this does not reproduce the entire confirmatory analysis pipeline. Figure pixel identity is not asserted. See [reproduction details and validation receipt](docs/reproducibility/README.md).

## Research artifacts

- [Generated evidence audit](docs/report/evidence_audit.md) and [saved audit JSON](results/report_audit.json).
- [Program v2 study summary](docs/v2/STUDY_SUMMARY.md), [preregistrations](prereg/) and [deviations](prereg/DEVIATIONS.md).
- [Completed context review](docs/research/context_review/COMPLETION.md), including rival explanations, source verification and limitations.
- `results/v2/` contains saved episode/cell data; `analysis/` contains analysis code; `civlab/` contains game/task logic and provider routing; `tests/` uses mock transports for offline checks.
- [Current handoff run log](RUNLOG.md). Older experiment-runner instructions are historical, not a request to restart jobs.

## Collecting new model responses

Fresh model replication is separate from saved-data reproduction. It needs provider access, the documented roster, prompts, task configurations, seeds and budget controls. Hosted responses may differ over time even with the same request. Live runs can consume allowance or money and are not performed by `tools.reproduce`.

The original v1 commands and narrative are preserved in the [historical README](docs/HISTORICAL_README_V1.md); current scope and limitations are in the linked review. API access alone does not guarantee the same numerical outputs.

## Citation and license

[CITATION.cff](CITATION.cff) · [MIT license](LICENSE).
