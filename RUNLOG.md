# Program v2 run log

**Authoritative.** Every agent reads the top block first and updates it at the end of every session
(AGENT_HANDBOOK.md §4). Entries use templates/SESSION_ENTRY.md. Mirrored to the vault note
`700 Research/Agent Civilizations/Program v2 Run Log.md` when an agent has vault access.

## Top block (always current)

```
NORTH STAR: Q0 — can game-theoretic lessons from multi-agent systems measurably improve everyday agents, across models?
CURRENT PHASE: 0 → shared pilot · LAST GATE PASSED: none (G0 pending smoke)
NEXT ACTION:
  1. [agent] When results/_phase0/smoke.csv exists (REQUEST_PHASE0 set 2026-09-25 06:23 UTC; runner now has
     timeouts + results/_runner/provider_errors.log): read it; fix failures (mistral + llama31_70b_nemotron had
     0 successful calls and gemini_38_flash stalled in the first attempt — check provider_errors.log); then
     python -m tools.freeze_roster --extra haiku45 ; python -m tools.check_free_tier ; record G0 below.
     Freezing roster.yaml unblocks the pilot jobs already in queue.yaml (runner picks them up within 15 min).
  2. [agent] Haiku pilot is running in Claude's cloud workspace (started 06:23 UTC, 452 cells); copy
     results/v2/*/haiku45/*.json into the repo when done.
  3. [agent] After the pilot: check G1 (harness, invalid rate < 10%, P6 positive control direction) and G3
     (calibration bands, docs/v2/records/*.md §2); turn knobs if needed; then write prereg/PREREG_A.md + PREREG_B.md
     and source the T5 phrase panel (prereg/phrase_sources.md).
BLOCKERS: none.
NEEDS ADI: none.
SCORECARD DRAFT: P1 – · P2 – · P3 – · P4 – · P5 – · P6 (pos. control) – · L1 – · L2 –
```

## Sessions (oldest first)

### 2026-09-23 · Session 0 · Claude (Cowork) · Planning
- **Goal:** turn the v1 critique into an executable cross-model plan (all links).
- **Done:** Program plan v2 written (docs/v2/PROGRAM_PLAN.md). Provider reachability tested: Claude's cloud workspace and the Cowork VM cannot reach openrouter.ai, api.groq.com, generativelanguage.googleapis.com, api.cerebras.ai, ollama.com (pypi.org works from the VM) → model calls must run on Adi's PC.
- **Next action:** red-team the plan.

### 2026-09-24 · Session 1 · Claude (Cowork) · Planning (red team)
- **Goal:** check every component serves Q0; prepare adversarial Q&A; revise the plan.
- **Done:** docs/v2/RED_TEAM_REVIEW.md; plan revised to v2.1 (Phase B priority; expert arm in T1/T3/T5; T5 phrase panel with a pre-registered rubric; T2 evidence+self-report and raw-history arms; capability-controlled L2; LLM-counterpart check; P6 as positive control; A1 golden and A2 longrun cut). Budget ≈ 56k calls, $0.
- **Next action:** Phase 0 setup.

### 2026-09-24 · Session 2 · Claude (Cowork) · Phase 0 build
- **Goal:** Phase 0 infrastructure (plan §4–§5).
- **Done:** folder access to the repo; v1 noisy experiment + docs zips applied (committed by Adi as f044fa8); harness written: civlab/{providers,router,parse,envload}.py, tools/{discover_models,bench_local,smoke,freeze_roster,install_hooks}.py, roster_candidates.yaml, tests; DECISIONS.md, PARKING_LOT.md, prereg/.
- **Problems:** (1) a key-status check printed the GROQ key into the chat (the .env had a UTF-8 BOM the check didn't handle) → Adi rotated keys and moved them to Windows user environment variables via tools\set_keys.ps1; .env deleted. Rule added: agents never read key values. (2) a VM `git status` left a stale .git/index.lock → removed (delete permission granted for the repo folder); rule: agents only use `git --no-optional-locks` read commands.
- **Findings (Phase 0 discovery, 2026-09-24):** reachable from the PC: gemini (61 models), mistral (46), nvidia (82), openrouter (458), ollama (running, 0 models). groq → 401. NVIDIA has no Llama 3.1-8B/3.3-70B; Groq is the only free source for the Llama line, Qwen3-32B and gpt-oss-120b. Gemini smoke replies well-formed (first 5 calls).
- **Gate:** none.
- **Next action:** see top block.

### 2026-09-24 · Session 3 · Claude (Cowork) · Autonomy + handbook
- **Goal:** let agents run the program without the owner, at $0, with full documentation.
- **Done:** AGENT_HANDBOOK.md (+ AGENTS.md/CLAUDE.md pointers); free-tier guard in code (civlab/free_tier.py, enforced in Router; tools/check_free_tier.py); queue runner tools/run_queue.py (resumable cells, RPD parking, failure cap, STOP/RESTART/PAUSE flags, status heartbeat); Windows scheduled-task scripts (runner_service.ps1 with REQUEST_PHASE0/REQUEST_TESTS flags, autosync.ps1, install_runner.ps1, uninstall_runner.ps1); experiments/v2 interface + _selftest; roster_candidates revised (pinned dated ids; NVIDIA/OpenRouter-free fallbacks; nemotron_super, lfm_2b, ministral_8b, gemini_38_flash added); tools print fixes; smoke --include-claude; templates/; docs/v2/ copies of the plan and red-team review. Offline tests: 11 pass.
- **Next action:** see top block.

### 2026-09-25 · Session 4 · Claude (Cowork) · Phase 0 discovery
- **Goal:** get every provider working and resolve the roster candidates (G0 inputs).
- **Done:** tools/check_keys.py (tests each key live without revealing it). Adi's run: all 5 keys accepted (Gemini key uses Google's newer "AQ." prefix; checker updated). Discovery: groq 11 models, gemini 61, mistral 46, nvidia 82, ollama 4, openrouter 460. Bench: llama2:7b-chat 72 tok/s, llama3:8b 61, qwen2.5:7b 63, llama3.2:3b 131 (GPU).
- **Findings:** Groq no longer serves any Llama chat model (catalog: qwen3.8-27b, gpt-oss-20b/120b, allam-2-7b, guard/audio models); no free host has Llama 3.1-8B/3.3-70B/4-Scout. Preliminary smoke (first-try, from call logs): gpt-oss-20b 20/20, gpt-oss-120b 14/14, gemini-3.8-flash 1/1, llama3:8b 18/20, llama2:7b 16/20, nemotron-3-super 2/12 (emits long reasoning and hits max_tokens).
- **Changes:** candidates revised (Meta line → local llama2/3/3.1/3.2 + NVIDIA Llama-3.1-70B Nemotron tune; Qwen → Qwen3.8-27B on Groq; nemotron thinking disabled via chat_template_kwargs); local cap 3→5; smoke now scores validity after one format re-ask (same policy as the experiments). DECISIONS #6–#8.
- **Gate:** none. **Next action:** see top block.

### 2026-09-25 · Session 5 · Claude (Cowork) · Phase B/A build + pilot queued
- **Goal:** build every experiment module (Handbook §6 "Phase B/A build"), start the shared pilot. Serves L1–L4.
- **Done:** Adi pulled llama3.1:8b and installed the scheduled tasks (runner every 15 min, autosync every 2 h). Built civlab/everyday/{common,t1_negotiation,t2_trust,t3_budget,t4_problems,t5_refund}.py and experiments/v2/{t1..t5, a1..a6}.py with arm texts verbatim from the plan; strict parsing with one re-ask then a flagged random action. tests/test_everyday.py: bot behaviour, scripted-policy sanity tests (good policy near top, bad near bottom) for T1/T2/T3/T5, end-to-end cells for every module, cell counts match plan §10.1. 23/23 tests pass in the cloud and on the PC's VM. Experiment records created in docs/v2/records/. queue.yaml now holds the pilot jobs (ollama_llama31_8b + haiku45). Haiku smoke passed from the cloud (20/20; results/_phase0/smoke_haiku45.csv); Haiku pilot started in the cloud workspace.
- **Problems:** the first REQUEST_PHASE0 smoke stalled after ~10 min (06:09 UTC) with mistral/nvidia-70b/gemini-3.8 unfinished, and the service instance ended without writing smoke.csv. Fixes: provider attempts log to results/_runner/provider_errors.log; httpx timeout 60 s; Retry-After capped at 90 s; smoke uses 3 attempts and a 480 s per-model budget; runner_service runs Phase 0 tools under hard wall-clock timeouts; run_queue caps each cell at 45 min. REQUEST_PHASE0 re-set.
- **Early observation (not a finding):** Haiku T5 benign-phrase arms: 20/20 correct (entitled refunded, manipulative given store credit) — T5 may be at ceiling for Haiku; G3 needs only 1 of 2 pilot models in band.
- **Gate:** none. **Next action:** top block.
