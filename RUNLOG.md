# Program v2 run log

**Authoritative.** Every agent reads the top block first and updates it at the end of every session
(AGENT_HANDBOOK.md §4). Entries use templates/SESSION_ENTRY.md. Mirrored to the vault note
`700 Research/Agent Civilizations/Program v2 Run Log.md` when an agent has vault access.

## Top block (always current)

```
NORTH STAR: Q0 — can game-theoretic lessons from multi-agent systems measurably improve everyday agents, across models?
CURRENT PHASE: FULL RUN (Phase B priority 1, Phase A priority 2, robustness priority 3)
LAST GATE PASSED: G0, G1, G3 (pilot_check 2026-09-25 11:37 UTC, all five tasks in band); PREREG committed de3f42b (pushed 03:55 local)
NEXT ACTION (each session):
  1. Read results/_runner/status.json + provider_errors.log; investigate *.failed.json; leave quota-parked models alone.
  2. Keep the Haiku cloud runner going (/home/claude/wk, `python3 -m tools.run_queue --include-claude`; only runs while a
     Claude session is active); periodically tar results/v2/*/haiku45/*.json into the repo (see Session 9).
  3. Analysis code is written and tested (Session 10, DECISIONS #19). Optionally run `python3 -m analysis.scorecard --interim`
     (writes only to results/_runner/interim/). When every cell is done: `python3 -m analysis.scorecard` (confirmatory),
     then the independent verification pass (a fresh agent re-derives 3+ headline numbers from raw cells).
BLOCKERS: none.  NEEDS ADI: none (optional: read prereg/PREREG_B.md).
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

### 2026-09-25 · Session 6 · Claude (Cowork, scheduled check-in) · Gate G0 + pilot start
- **Goal:** read the Phase 0 smoke, freeze the roster, start the pilot (L1–L4 prerequisites).
- **Runner status seen:** REQUEST_PHASE0 completed 23:51 local with the new timeouts; smoke.csv written.
- **Findings (smoke, valid rate after one re-ask):** pass: qwen38_27b 1.0, gptoss_20b 1.0, gptoss_120b 1.0, ministral_8b 1.0, nemotron_super 1.0 (thinking disabled), llama2 7B 1.0 (raw 0.8), llama3 8B 1.0 (raw 0.9), llama3.1 8B 1.0, qwen2.5 7B 1.0, llama3.2 3B 1.0; haiku45 1.0 (cloud). Fail: llama31_70b_nemotron (NVIDIA 404), gemini-2.5-flash (404 retired), gemini-3.8-flash (free-tier quota 429; 3/20), gemma (AI Studio 500/503 — transient), mistral_small (429 on every call), lfm_2b (empty replies).
- **Done:** G0 PASS — `python -m tools.freeze_roster --extra haiku45` → roster.yaml (11 models, 6 families); `check_free_tier` PASS; dry-run shows 452 pilot cells for ollama_llama31_8b. Candidates revised for a pre-PREREG re-test (gemma, mistral_small at rpm 6, gemini_flash_lite); REQUEST_PHASE0 set. analysis/pilot_check.py written (G1/G3 automated).
- **Problems:** (1) Haiku pilot process in the cloud died while the session idled (cloud workspace reclaims idle processes); restarted — it resumes from cache. (2) Haiku T1 pilot showed a design problem: control surplus 0.09 (below band) and the $20 hardball step made ≤ $880 unreachable in 6 turns → fair concession 0.40 → 0.55 (plan knob) and hardball step $40; old Haiku T1 cells deleted; tests updated (23 pass). DECISIONS #9–#11. (3) Test suite polluted a local quota counter (default RPD for the mock "groq" entry) → tests now set rpd None.
- **Early observations (not findings):** Haiku T5 control and benign arms 100% correct (likely ceiling); Haiku T1 answer_only beat control on surplus under the old bots (positive control may not hold for negotiation — re-check after the fix).
- **Gate:** G0 PASS. **Next action:** top block.

### 2026-09-25 · Session 7 · Claude (Cowork, scheduled check-in) · Pilot round 1 results + knob round 2
- **Goal:** G1/G3 on the pilot (plan §6).
- **Runner status seen:** Llama 3.1 8B pilot finished (all 452 cells, 0 failed; runner idle since 02:07 local). Haiku pilot in the cloud had died when the session idled; restarted.
- **Findings — pilot round 1, ollama_llama31_8b (calibration only, not results):** invalid-action rate 0–1% everywhere (G1 part 1 OK). Control-arm bands: T1 surplus 0.121 (out; Haiku 0.154 in), T2 lifetime post-betrayal acc 0.708 (in), T3 control survival 0/3 (in), T4 single-sample acc 0.779 (Haiku 0.971; pooled 0.875 out), T5 wrongful refunds 0% (out; Haiku also 0%). Sanity look at other arms: T2 game 0.75 > lifetime 0.71 > rawhistory 0.65, evidence_selfreport 0.52 ≈ control 0.50; A4 fitness anon +18.1, lifetime AllD −7.6, lifetime stealth +3.7, window stealth −3.1; A3 Llama cooperates only 0.33 with AllC (unlike Haiku). T3: team "Cobalt" requests 80–100 in week 1 in every arm (label artefact constant across arms; noted).
- **Done:** knob round 2 for T5 and T4; T4b positive-control arm; pilot_check updated; roster amended (+gemini_flash_lite); tests 25/25 (cloud + VM); round-1 T4/T5 Llama cells moved to results/v2/_superseded_pilot_r1/; stale Haiku T4/T5 cells removed; run_queue --dry-run no longer consumes the RESTART flag (it crashed in the VM, which lacks delete permission). DECISIONS #12–#15.
- **Gate:** G1 pending round 2 (positive control), G3 pending T4/T5. **Next action:** top block.


### 2026-09-25 · Session 8 · Claude (Cowork, scheduled check-in) · Pilot round 2 → round 3 + pre-registration
- **Goal:** decide G1/G3, finish calibration, write the pre-registration (plan §6).
- **Findings (pilot round 2, calibration only):** Llama T4 single-sample 0.696 (in band), T4b answer-only 0.333 vs first reasoning sample 0.729 → **G1 PASS** (positive control detected). T5 round 2: control wrongful refunds still 0% on Llama and Haiku; rubric-harmful arms H2 0.9 / H3 1.0 / H1 0.1 (Llama), H1 0.6 / H2 0.5 / H3 0.8 (Haiku, old H2); benign, game, expert, placebo 0%; Llama answer_only 1.0 wrongful refunds (deliberation protects policy-following — secondary).
- **Done:** T5 round 3 (last): H1+game / H1+expert / H1+placebo arms; H2 replaced with a verbatim published instruction; pilot_check T5 band on the H1 base arm; phrase sourcing (prereg/phrase_sources.md, grades A/B); PREREG_A.md and PREREG_B.md written with roster table and code hashes; queue_full.yaml prepared (inactive); plan amendments v2.2 appended to docs/v2/PROGRAM_PLAN.md; DECISIONS #16–#18. Haiku pilot restarted (single process).
- **Gate:** G1 PASS; G3: T1 (Haiku 0.154), T2, T3, T4 in band; T5 pending round 3. **Next action:** top block.

### 2026-09-25 · Session 9 · Claude (Cowork, scheduled check-in) · Gates passed → full run started
- **Goal:** confirm the pre-registration commit, pass G3, start the full run (plan §6).
- **Done:** prereg/PREREG_A.md + PREREG_B.md + phrase_sources.md are in commit de3f42b (autosync, pushed 2026-09-25 03:55 -0700). T5 round-3 pilot cells finished minutes before that commit (declared pilot data). Haiku pilot cells (489) copied into the repo via results/_runner/haiku45_pilot.tgz. `python -m analysis.pilot_check --models ollama_llama31_8b,haiku45`: **G1 PASS; G3 PASS for T1 (Haiku 0.154), T2, T3, T4 (pooled 0.831), T5 (H1 base arm 0.1 / 0.6)**. Full queue activated (queue.yaml from queue_full.yaml + temperature-sensitivity job + LLM-counterpart robustness job); roster gained 4 robustness-only temperature keys (excluded from `models: all`); run_queue patched accordingly; c1_counterpart module written + tested (counterpart = nemotron_super; focal ollama_llama31_8b, qwen38_27b, gemini_flash_lite, gptoss_20b — Haiku cannot be focal because the cloud cannot reach NVIDIA). Dry run: 5,624 pending PC cells across 14 roster keys; Haiku (cloud) 71 pending cells. Tests 26/26.
- **Gate:** G1, G3 PASS. **Next action:** top block.

### 2026-09-25 · Session 10 · Claude (Cowork, scheduled check-in) · Full-run monitoring: free-tier daily limits
- **Goal:** keep the full run moving; handle provider errors; sync Haiku cells.
- **Observed:** PC progress 3,880 / 6,460 cells (07:15 local). No *.failed.json. 99 *.attempts.json caused by (a) Groq gpt-oss-120b daily token cap ("tokens per day (TPD): Limit 200000"), (b) Gemini flash-lite daily quota ("exceeded your current quota"), (c) NVIDIA nemotron_super 429 Too Many Requests + 503 overloaded. The old code retried daily-quota 429s as if they were per-minute limits, burning attempts.
- **Done:** civlab/providers.py — a 429 whose body names a daily/TPD/RPD/quota limit now raises QuotaExhausted, which propagates out of the retry loop so run_queue parks that model until the next day (no failure counted). roster.yaml — nemotron_super rpm 15, concurrency 1. The 99 attempts files moved to results/_runner/cleared_attempts/ (retry counters reset; no results touched). Tests 26/26. results/_runner/RESTART set so the running runner exits after its current cells and the next 15-min service tick starts one with the patched code. Same patch mirrored into the Haiku cloud copy; Haiku runner restarted (48 pending A-battery cells). Haiku cells synced: 512 in the repo (results/_runner/haiku45_cells.tgz, extracted without overwriting).
- **Implication:** with Groq capped at 200k tokens/day for gpt-oss-120b and Gemini's daily quota, the remaining cells for those models will take several days. This is expected and within free tiers; no action needed from Adi. Option if it becomes the bottleneck (logged in PARKING_LOT, not adopted): serve gptoss_20b via NVIDIA (same open weights) as a declared deviation.
- **Analysis code (same session):** analysis/v2data.py (loading + PREREG_B §7 validity), everyday_effects.py (§6.1–6.4 + §7 robustness + secondary table), fingerprints.py (PREREG_A §2–§4), link2.py (§6.5), scorecard.py (assembles all; prints the SCORECARD line). Implementation choices where the prereg is silent are fixed in DECISIONS #19 before the run completes. tests/test_analysis.py: 7 synthetic known-answer tests; whole suite 33/33 in the VM. Interim smoke on live partial data (`python3 -m analysis.scorecard --interim`, outputs in git-ignored results/_runner/interim/) runs end to end.
- **Design risks seen in interim data (observations, not findings; no prereg change):** (1) H-B6: single-sample T4 accuracy spans 0.21–1.00, and no model yet has 4 others within ±0.10, so under the §6.3 rule P5 may end "not testable". (2) T3: week-8 survival is 0 in control, game_U, placebo and expert for every model so far (only the game_T transparency panel keeps pools alive), so H-B5/E2 have zero variance and will likely read "does not transfer". (3) Invalid-action rates above 10% already exclude ollama_llama2_7b from T1, ollama_llama32_3b from T4b and ollama_llama3_8b from T5 (PREREG_B §7).
- **Next action:** top block.
