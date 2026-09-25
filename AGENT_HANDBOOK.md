# Agent Handbook: Agent Civ Lab, Program v2

**Read this whole file before doing anything.** It tells any agent (any model, any session, any environment) how to pick up this project, keep it moving without the owner, stay at $0, and leave a record good enough that a stranger could reproduce every result.

- **Owner:** Adi. **Repo:** `C:\Repos\agent-civ-lab` = GitHub `ApriCuz54/agent-civ-lab`.
- **Handbook version:** 2026-09-24.
- **Source of truth for "where are we":** the top block of `RUNLOG.md`. It overrides the snapshot in §3.

---

## 0. The rules that override everything else

1. **Stay at $0.** Only run models that pass `python -m tools.check_free_tier`. Never add a payment method, attach billing, upgrade a plan, buy credit, or call a paid model or endpoint. The code enforces this (`civlab/free_tier.py`); don't weaken it. §5 has the details.
2. **Never read, print, copy or move API keys.** Keys live only in Windows user environment variables on Adi's PC. Don't open `.env` files or print environment variables. If you must check that a key exists, print only `True`/`False`, or the first 4 characters and the length. *(On 2026-09-24 an agent printed a key by accident, and the key had to be rotated.)*
3. **Write everything down.** Every session appends an entry to `RUNLOG.md` and updates the relevant experiment record. If it isn't written down, it didn't happen. §7 has the standard.
4. **Serve the north star.** Before adding any experiment, arm or analysis, apply the Q0 test (§1.3). If it fails, add a line to `PARKING_LOT.md` and move on.
5. **Pre-registration is binding.** After `prereg/PREREG_*.md` is committed, any change to prompts, arms, metrics, exclusions or verdict rules is logged in `prereg/DEVIATIONS.md` with a reason. Never change a hypothesis to fit the data.
6. **Never hand-edit results.** Every number in a write-up comes from a script in `analysis/`. Never delete caches, result cells or logs. Never loosen the served-model check in `civlab/providers.py`.
7. **Git hygiene.**
   - Agents don't run git commands that write. The `autosync` scheduled task commits and pushes.
   - For reading, use `git --no-optional-locks log/status/diff`. Plain `git status` from the Cowork VM leaves a `.git/index.lock` behind, and that breaks the next commit.
   - Never force-push. Never rewrite history.
8. **Report honestly.** Nulls, failures and mistakes go in the record in plain words. Corrections go in the lab record's audit-corrections appendix.
9. **Know when to stop and ask Adi.** §9 lists exactly when. Otherwise, proceed on your own.

---

## 1. What the project is (one page)

### 1.1 The question (Q0)

> Can what we learn from multi-agent systems, viewed through game theory, be turned into instructions and system designs that measurably improve AI agents on everyday tasks, across models and not just on one?

### 1.2 How it gets answered

Four links must hold, and every experiment tests at least one:

- **L1 Generality.** The game behaviors seen on Haiku in v1 appear across models.
- **L2 Prediction.** A model's game fingerprint predicts its behavior on matching everyday tasks. Tested with partial correlations controlling for capability.
- **L3 Transfer.** Game-derived interventions improve everyday tasks and beat a length-matched placebo. They should ideally also beat domain-expert advice.
- **L4 Value.** The gain is large enough to matter to a user.

Six principles are under test:

| # | Principle | Everyday task |
|---|---|---|
| P1 | Wording risk | T1 negotiation, T5 refund phrase panel |
| P2 | Reciprocity and the shadow of the future | T1, T5 |
| P3 | Recent, environment-computed reputation | T2 worker trust |
| P4 | Collective-consequence framing | T3 shared budget |
| P5 | Diversity over replication | T4 ensembles |
| P6 | Deliberation, used as the **positive control** | T1, T5 |

The final deliverable is a **scorecard**. Each principle gets one of: "transfers, beats expert", "transfers", "partial", or "does not transfer". Each comes with effect sizes in user units.

### 1.3 The Q0 test

Before adding any work, write this line in `RUNLOG.md`:

> "Tests link L_ for principle P_; the result that would change the scorecard is ___."

If you can't fill in the blank, the work doesn't happen.

### 1.4 Documents to read, in this order

| Order | File | What it is |
|---|---|---|
| 1 | `AGENT_HANDBOOK.md` | This file: how to work |
| 2 | `RUNLOG.md` | Where we are, the next action, and the history of every session |
| 3 | `docs/v2/PROGRAM_PLAN.md` | The executable plan v2.1: every experiment, arm, prompt, gate, statistic and verdict rule. **Specs come from here. Don't invent them** |
| 4 | `docs/v2/RED_TEAM_REVIEW.md` | Why the design looks the way it does, and 24 adversarial questions the work must survive |
| 5 | `docs/lab_record.md` | Everything done in v1 (2026-09-12 to 09-23): setups, results, corrections |
| 6 | `DECISIONS.md`, `PARKING_LOT.md`, `prereg/` | Decisions, parked ideas, pre-registration and deviations |

Adi's Obsidian vault (`Claude-Vault/700 Research/Agent Civilizations/`) mirrors these for humans. If you have access to it, mirror your `RUNLOG.md` entry into `Program v2 Run Log.md`. **The repo is authoritative.**

---

## 2. Where things run (read carefully; this is what makes autonomy work)

Three environments exist. Only **Adi's Windows PC** can reach the model providers. The Claude cloud workspace and the Cowork VM were both tested on 2026-09-23 and can't connect.

| Environment | How you get there | Can | Cannot |
|---|---|---|---|
| **Windows PC (the host)** | Only through the scheduled tasks below, or through Adi typing commands | Call every provider; read the keys (user env vars); run Ollama; `git push` (credentials cached) | Be driven directly by an agent |
| **Cowork VM on the PC** | A Claude session with folder access to `C:\Repos\agent-civ-lab` (appears as `$HOME/mnt/agent-civ-lab`) | Read and write every repo file; run Python for offline tests and analysis (`pip install` works; pypi is reachable); create flag files | Reach providers; see keys; run Windows commands; use git for writing |
| **Claude cloud workspace** | Any Claude session | Run **Claude models (Haiku) via the subscription SDK**; heavy analysis and figures; publish artifacts | Reach providers; see the repo except by staging files through device tools |

**The autonomy loop.** Agents never need to type on the Windows PC:

```
Agent (Cowork VM or cloud)                       Windows PC (scheduled tasks, no human)
───────────────────────────                      ─────────────────────────────────────────
writes experiments/v2/*.py, tests  ───────────▶  agent-civ-lab-runner (every 15 min):
edits queue.yaml (adds a job)                      · consumes REQUEST_* flags (Phase 0 checks, tests)
creates results/_runner/RESTART                    · python -m tools.run_queue  → results/v2/...
reads results/_runner/status.json  ◀───────────    · then autosync → git commit + push
reads results/v2/**/*.json, logs   ◀───────────  agent-civ-lab-autosync (every 2 h): commit + push
writes analysis, records, RUNLOG
```

**Control files** (in `results/_runner/`, not committed):

| File | Who creates it | Effect |
|---|---|---|
| `RESTART` | agent | The runner exits after its current cells. The next 15-minute trigger starts it with fresh code and queue |
| `STOP` | agent or Adi | The runner halts and stays halted until the file is removed. Use it when something is wrong |
| `PAUSE` | Adi (or an agent in an emergency) | The runner won't start at all |
| `REQUEST_PHASE0` | agent | On the next trigger, re-runs `discover_models`, `bench_local` and `smoke`. Output goes to `phase0_*.txt` |
| `REQUEST_TESTS` | agent | On the next trigger, runs `pytest -q tests` on Windows. Output goes to `tests.txt` |
| `status.json` | runner | Heartbeat: progress per experiment × model, parked models, failed cells, last error |
| `runner.log`, `service.log`, `autosync.log` | scripts | Logs |

**Claude models (Haiku 4.5)** can't run on the PC, because the SDK login lives in the cloud workspace. To run Haiku cells:

1. Get the current code into the cloud workspace. Clone from GitHub if reachable; otherwise stage the files through the device tools.
2. Run `python -m tools.run_queue --include-claude --models haiku45`.
3. Copy `results/v2/<exp>/haiku45/*.json` back into the repo with the device commit tool.

Haiku uses Adi's existing subscription. It's optional and never on the critical path.

---

## 3. Current state (snapshot 2026-09-24; `RUNLOG.md` supersedes this)

- **Phase 0 (setup), in progress.**
  - Providers reachable from the PC: Google AI Studio, Mistral, NVIDIA, OpenRouter, and Ollama (running, but **no models pulled yet**).
  - **Groq key rejected (401)**. Adi must fix it. Five roster models depend on Groq.
- **Harness built and tested offline (11 tests pass).** It includes the provider client, router, strict parsers, free-tier guard, discovery, benchmark, smoke, freeze, queue runner and the Windows scheduled-task scripts. The **Phase A/B experiment modules are not written yet.**
- **Next agent work (in order):**
  1. After Adi fixes Groq and Ollama: create `REQUEST_PHASE0`, or ask Adi to run the three tools. Read `results/_phase0/smoke.csv`. Smoke Haiku from the cloud workspace. Freeze the roster (`python -m tools.freeze_roster --extra haiku45`). Record gate G0.
  2. Adi installs the scheduled tasks, one time: `powershell -ExecutionPolicy Bypass -File tools\install_runner.ps1`.
  3. Build the Phase B modules (T1–T5), then the Phase A battery, per plan §7–§8 and §6 below.

---

## 4. Session protocol (every agent, every time)

**Start of session (5–10 minutes):**

1. Read this handbook (all of it the first time; §0 and §3 on later visits).
2. Read the `RUNLOG.md` top block and the last 3 session entries.
3. Work out which environment you are in (§2). Check you can see the repo (Cowork: `ls $HOME/mnt/agent-civ-lab`).
4. Read `results/_runner/status.json` and the tail of `results/_runner/runner.log`, to see progress, parked models and failed cells.
5. Do the **NEXT ACTION** from the top block. If it's blocked, write down why and pick the next unblocked item from the phase playbook (§6).

**During the session:**

- Keep code runnable at every save. Write new files, test offline, then wire them in. Autosync may push at any moment.
- Test offline before anything touches real models. Use `python -m pytest -q tests` (Cowork VM or cloud), or create `REQUEST_TESTS` to run the tests on Windows.
- When you add a queue job, run `python -m tools.run_queue --dry-run` in the VM first to confirm the cell counts, then create `RESTART`.

**End of session (always, even if the session was cut short):**

1. Append a session entry to `RUNLOG.md` using `templates/SESSION_ENTRY.md`.
2. Update the **top block**: current phase, last gate, the exact NEXT ACTION, blockers, and the scorecard draft.
3. Update each touched experiment record in `docs/v2/records/`.
4. Record decisions (`DECISIONS.md`, with a "why" line Adi can fill in or edit) and deviations (`prereg/DEVIATIONS.md`).
5. If you have vault access, mirror the entry into the vault run log.

---

## 5. Free-tier policy (how we stay at $0)

**How money could be spent, and how each way is blocked:**

| Risk | Block |
|---|---|
| Calling a paid model (e.g. a non-`:free` OpenRouter model, which spends purchased credit) | Code: `civlab/free_tier.py`. The router refuses any entry that fails the rules, and the runner refuses to start if `tools.check_free_tier` fails |
| Pointing a provider at a different (paid) endpoint | Code: custom base URLs are refused except localhost |
| Billing attached by a human (Google Cloud billing on the AI Studio key's project; Groq Developer tier; Mistral paid plan; any card) | **Agents never do this and never ask for it.** Free tiers answer over-limit requests with HTTP 429 rather than charging, as long as no billing is attached |
| Exceeding free limits | Harmless (429). The client also keeps a persisted requests-per-day counter per model (`results/_quota/`) and parks a model when the counter hits its cap |

**Allowed providers** (free tiers as published Jun–Sep 2026; re-verify if anything changes):

| Provider | Terms |
|---|---|
| Groq | Free, no card |
| Google AI Studio | Free while there's no billing |
| Mistral | Free "Experiment" plan; prompts may be used for training, which is fine because we send no personal data |
| NVIDIA NIM | Free developer access, rate-limited |
| OpenRouter | `:free` variants only |
| Cerebras | Free tier |
| Ollama | Local |
| Claude SDK | Existing subscription; optional |

**Before any full run:** `python -m tools.check_free_tier` must print `RESULT: PASS`. The runner checks this too.

**If a provider changes its free terms,** park that provider's models: remove them from the queue job's `models` list and log a deviation. Substitute per plan §3.3. Never "just pay a little".

---

## 6. Phase playbook (what to do, with done-criteria)

Specs for every experiment are in `docs/v2/PROGRAM_PLAN.md` (plan). Section numbers below refer to it.

### Phase 0: Setup (gate G0)

| Step | Who | How | Done when |
|---|---|---|---|
| 0.1 Fix the Groq key | **Adi** | New key at console.groq.com, `tools\set_keys.ps1`, new shell | `discover_models` shows groq `ok` |
| 0.2 Pull Ollama models | **Adi** | `ollama pull llama2:7b-chat`, `llama3:8b`, `qwen2.5:7b`, `llama3.2:3b` | `models_ollama.json` isn't empty |
| 0.3 Discovery, benchmark, smoke | Adi now; agents later via `REQUEST_PHASE0` | `python -m tools.discover_models`, `bench_local`, `smoke` | `results/_phase0/smoke.csv` covers every resolved candidate |
| 0.4 Fix failures | agent | Read `smoke.csv` `first_error`. Typical fixes: an unsupported `extra` param (e.g. `reasoning_effort`) → edit that source in `roster_candidates.yaml`; a served-model mismatch → add `served_aliases` only if it's the *same* model; low valid-rate → the model is excluded (don't tune prompts per model) | Every candidate either passes or has a written reason |
| 0.5 Haiku smoke | agent (cloud) | `python -m tools.smoke --include-claude --models haiku45` from the cloud workspace (with roster_draft.yaml copied there) | Haiku valid-rate recorded |
| 0.6 Freeze the roster | agent | `python -m tools.freeze_roster --extra haiku45` (VM is fine), then `python -m tools.check_free_tier` | `roster.yaml` exists with ≥ 8 models; G0 recorded in RUNLOG |
| 0.7 Install the scheduled tasks | **Adi (once)** | `powershell -ExecutionPolicy Bypass -File tools\install_runner.ps1` | `service.log` shows the runner starting every 15 min |

### Phase B/A build (agents; no model calls)

For each task T1–T5 (plan §8), then the A1–A6 battery (plan §7):

1. Write `experiments/v2/<id>_<name>.py` with `NAME`, `cells(config, model)` and `async run_cell(router, model, cell, config)`. `experiments/v2/_selftest.py` is the minimal example. **Prompts and arm texts are copied verbatim from the plan.**
2. Put scripted counterparts (sellers, workers, customers) in `civlab/everyday/`. They must be pure Python and deterministic given the seed.
3. Use the strict parsers in `civlab/parse.py`. On invalid output: re-ask once with the format reminder, then take a random valid action and record `invalid=1` (plan §1).
4. Add tests in `tests/`:
   - bots behave as specified;
   - **the scripted-policy sanity test**: a known-good policy scores near the top and a known-bad policy near the bottom (plan §8.8);
   - a full cell runs end to end with `MockTransport`.
5. Create the experiment record `docs/v2/records/<id>.md` from `templates/EXPERIMENT_RECORD.md`.
6. For T5, source the phrase panel: find each phrase in a public customer-service prompt or template, and log the URLs in `prereg/phrase_sources.md` (plan §8.6).

**Done when:** all modules exist, the tests pass in the VM **and** on Windows (via `REQUEST_TESTS`), and `run_queue --dry-run` shows the expected cell counts (plan §10.1).

### Shared pilot (gates G1 and G3)

1. Add the pilot jobs to `queue.yaml`: every B task plus the A battery, on the two pilot models (plan §6; `llama31_8b` + `haiku45`, with Haiku run from the cloud). Mark them `phase: pilot`. Create `RESTART`.
2. When they're done, check **G1** (harness OK, invalid rate < 10%, P6 positive control in the expected direction) and **G3** (each task's control arm is inside its calibration band, plan §8). Turn knobs as the plan specifies, at most 3 rounds, and log each round.

### Pre-registration (binding)

1. Write `prereg/PREREG_A.md` and `prereg/PREREG_B.md` **from the plan, adding no new content**: hypotheses H-A1…6, H-B1…10 and E1–E3; metrics; exclusions; verdict rules; frozen prompt texts; the phrase panel with sources; knob values.
2. Wait until `git --no-optional-locks log -1 -- prereg/` shows the files committed (autosync, or push them sooner by asking Adi). **No full-run job may be queued before that commit exists.**
3. Adi's review of the pre-registration is recommended but doesn't block. Note it under "Needs Adi (optional)".

### Full run

1. Add the full jobs. Phase B gets `priority: 1`, Phase A `priority: 2`, models `all`. Queue the LLM-counterpart check (plan §8.7) after Phase B. Create `RESTART`.
2. Each session:
   - read `status.json` and log the progress;
   - investigate every `*.failed.json`, fix the cause, delete only the `.failed.json` and `.attempts.json` files to retry, and log what you did;
   - leave quota-parked models alone; they resume tomorrow.
3. Run the Haiku cells from the cloud workspace when convenient.

### Analysis and write-up

1. Build `analysis/everyday_effects.py`, `fingerprints.py`, `link2.py` and `scorecard.py` exactly as plan §9 specifies (hierarchical bootstrap, Holm families, partial Spearman, positive-control rule).
2. Run an **independent verification pass**: a separate agent re-computes every reported number from the result files.
3. Write:
   - the lab record v2 (chronological, same style as `docs/lab_record.md`);
   - paper v2 (`docs/paper_draft.md` updated);
   - the playbook page;
   - LinkedIn and résumé drafts, as **drafts only**.

---

## 7. Documentation standard

Write for a stranger who has only the repo. Be specific: exact commands, exact model ids, counts, dates, file paths. Every number comes from a script, and you say which one. Say what you *didn't* do or couldn't verify.

| What | Where | When |
|---|---|---|
| Session entry (goal, done, runner status, findings, problems, gate, deviations, needs-Adi, next action) | `RUNLOG.md` (template `templates/SESSION_ENTRY.md`) | End of every session |
| Top block (phase, last gate, NEXT ACTION, blockers, scorecard) | `RUNLOG.md` top | End of every session |
| Per-experiment record: **goal and link, setup, execution log, findings, conclusion, deviations** | `docs/v2/records/<id>.md` (template `templates/EXPERIMENT_RECORD.md`) | Whenever the experiment is touched |
| Design decisions and why | `DECISIONS.md` | When made |
| Changes after pre-registration | `prereg/DEVIATIONS.md` | When made |
| Ideas that failed the Q0 test | `PARKING_LOT.md` | When raised |
| Gate results, with evidence (file paths, numbers) | RUNLOG session entry, plus a North Star check (plan §12) at G0–G4 | At each gate |

**The North Star check** at every gate answers five questions:

1. Which links did this inform?
2. What changed in the scorecard?
3. Is any planned work no longer informative? Drop it.
4. Did anything new come up? Apply the Q0 test.
5. Are we on budget and schedule?

---

## 8. Command reference (run from the repo root)

| Command | Where | Purpose |
|---|---|---|
| `python -m pytest -q tests` | VM / cloud / Windows | Offline tests (no network) |
| `python -m tools.discover_models` | Windows | List live models and resolve candidates → `roster_draft.yaml` |
| `python -m tools.bench_local` | Windows | Ollama speed test; keeps models at ≥ 12 tok/s, at most 3 |
| `python -m tools.smoke [--models a,b]` | Windows | 20 probe calls per model → `results/_phase0/smoke.csv` |
| `python -m tools.freeze_roster [--extra haiku45] [--drop k]` | VM / Windows | Gate G0 → `roster.yaml` (requires ≥ 8 models) |
| `python -m tools.check_free_tier` | anywhere | $0 audit (must PASS) |
| `python -m tools.run_queue --dry-run` | VM | Show pending cells; no calls |
| `python -m tools.run_queue` | Windows (via scheduled task) | Run the queue |
| `python -m tools.run_queue --include-claude --models haiku45` | cloud | Run the Haiku cells |
| `powershell -ExecutionPolicy Bypass -File tools\install_runner.ps1` | Windows (Adi, once) | Install the scheduled tasks |
| `powershell -ExecutionPolicy Bypass -File tools\set_keys.ps1` | Windows (Adi) | Set keys at a hidden prompt |
| `python -m tools.install_hooks` | Windows (once) | Pre-commit key scanner |

---

## 9. When to stop and write "NEEDS ADI"

Write a `Needs Adi:` line in the RUNLOG top block, with exactly what and why, and **do not do it yourself**, when a task requires any of the following:

- money, billing, a payment method, credit, or a plan upgrade (the answer is always no; find a free substitute);
- a new account, a new key, a rotated key, or anything typed on the Windows PC (Ollama pulls, installing software, the scheduled-task install);
- deleting anything other than `.failed.json`/`.attempts.json` retry markers and runner flags;
- changing a pre-registered hypothesis or verdict rule (a *deviation* for procedure is fine if logged; changing what counts as success is not);
- publishing or sharing anything publicly (LinkedIn, arXiv, making artifacts public), or pushing to any remote other than `origin`;
- anything that would reveal a secret.

For everything else, including fixing bugs, substituting a failed model per plan §3.3, turning calibration knobs within plan limits, re-queuing failed cells and writing analysis, **proceed and document**.

---

## 10. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `401 Unauthorized` in discovery or smoke | Wrong or revoked key | NEEDS ADI: new key plus `set_keys.ps1` |
| `429` in logs | Free-tier rate limit | Nothing; the client backs off. If it persists, lower that model's `rpm`/`tpm` in `roster.yaml` and log a deviation |
| Model parked in `status.json` | Requests-per-day cap reached | Nothing; it resumes tomorrow |
| `HTTP 400` for one model | An unsupported parameter (often `reasoning_effort`) or a wrong model id | Fix the `extra` in `roster.yaml`/`roster_candidates.yaml`, then `REQUEST_PHASE0` or re-smoke that model |
| `served ... != ...` | The provider served a different model | Don't add an alias unless it's provably the same model; otherwise substitute the model |
| `models_ollama.json` is `[]` | Models not pulled, or Ollama not running | NEEDS ADI |
| No new lines in `service.log` for > 30 min | PC asleep or off, or tasks not installed | NEEDS ADI (power settings: `powercfg /change standby-timeout-ac 0`) |
| `COMMIT BLOCKED` in `autosync.log` | The pre-commit hook found a key-like string | Find and remove it from the file (never commit it); if it's a real key, NEEDS ADI to rotate it |
| `PUSH FAILED` in `autosync.log` | Remote diverged | Read the log. Never force-push. NEEDS ADI if a rebase can't resolve it |
| `.git/index.lock` exists | An interrupted git process | Autosync removes it after 10 min. Agents: don't run writing git commands |
| High invalid-reply rate for a model | The model can't follow the format | Pre-registered exclusion at > 10%. Report it; don't tune prompts per model |

---

## 11. File map (v2 additions)

```
AGENT_HANDBOOK.md        this file            RUNLOG.md       state + session history (authoritative)
AGENTS.md / CLAUDE.md    pointers to this file DECISIONS.md    decisions   PARKING_LOT.md  parked ideas
roster_candidates.yaml   candidate models      roster_draft.yaml  resolved (Phase 0)   roster.yaml  FROZEN at G0
queue.yaml               the work queue (jobs in priority order)
civlab/providers.py      multi-provider client (cache, rate limits, RPD counter, served-model check)
civlab/router.py         roster key → backend; calls civlab/free_tier.py before any call
civlab/parse.py          strict parsers (None on invalid)        civlab/envload.py  BOM-safe .env loader (legacy)
civlab/everyday/         scripted bots for T1–T5 (to be written)
experiments/v2/          experiment modules (cells + run_cell)   _selftest.py = minimal example
tools/                   discover_models, bench_local, smoke, freeze_roster, check_free_tier, run_queue,
                         runner_service.ps1, autosync.ps1, install_runner.ps1, uninstall_runner.ps1, set_keys.ps1
analysis/                v1 figure scripts; v2 analysis scripts (to be written)
prereg/                  PREREG_A/B (to be written), DEVIATIONS.md, phrase_sources.md
docs/                    lab_record.md (v1), paper_draft.md, v2/PROGRAM_PLAN.md, v2/RED_TEAM_REVIEW.md, v2/records/
templates/               EXPERIMENT_RECORD.md, SESSION_ENTRY.md
results/v2/<exp>/<model>/<cell_id>.json   one finished cell (committed)
results/_phase0/          discovery, benchmark, smoke outputs   results/_runner/  status, logs, flags (not committed)
```
