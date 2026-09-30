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
  2. Haiku (cloud) is COMPLETE: 560/560 cells in the repo (Session 11). Nothing to do unless a Haiku cell is found missing.
  3. Analysis code is written and tested (Session 10, DECISIONS #19). Optionally run `python3 -m analysis.scorecard --interim`
     (writes only to results/_runner/interim/). When every cell is done: `python3 -m analysis.scorecard` (confirmatory),
     then the independent verification pass (a fresh agent re-derives 3+ headline numbers from raw cells).
PHASE C: ACTIVE since PREREG_C commit 611852f (pushed 2026-09-27 20:09 -0700); job at priority 4 in queue.yaml; Haiku from the cloud workspace.
PHASE C CONFIRMATORY (8 models, DEVIATIONS #1): done 2026-09-28 → results/v2/_phase_c.md; verified (analysis/verify_phase_c.py). Addendum with the 4 cloud models once they finish (≈ 10-08/09).
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

### 2026-09-25 · Session 11 · Claude (Cowork, scheduled check-in) · Quota parking works; Groq OTPM pacing
- **Goal:** confirm the Session 10 patch took effect; keep both runners moving.
- **Observed:** the runner exited on RESTART at 07:40 (exit 3 = stopped by flag) and a new one started 07:52 (pid 27196). Daily-quota parking works: gemini_flash_lite, gptoss_120b and gptoss_20b are parked until tomorrow instead of burning attempts. PC progress 4,680 / 6,460 (09:00 local); no *.failed.json; 17 *.attempts.json (normal retry bookkeeping). Remaining errors: nemotron_super 429/503 (≈250–500 per hour even at rpm 15) and a new one — Groq qwen/qwen3.8-27b "output tokens per minute (OTPM): Limit 1000" (a reasoning model, so a few calls a minute exhaust it).
- **Done:** roster.yaml pacing only (no model, prompt or analysis change): qwen38_27b rpm 4 / conc 1; its robustness-only copies _t03/_t10 rpm 2 / conc 1 (same Groq model, separate limiters); nemotron_super rpm 15 → 10. Tests 33/33. RESTART flag set so the next service tick picks this up. Haiku cloud runner was dead (session idle) → restarted; 545 of its cells done, 15 A-battery cells pending → finished 16:09 UTC: **haiku45 complete, 560/560 cells, synced into the repo** (no failed cells). Lesson: re-committing a staged file under the *same* name delivered the stale earlier copy; use a new filename per transfer (here results/_runner/haiku45_cells_final.tgz) and verify the file count after extracting.
- **Interim scorecard** (`analysis.scorecard --interim`, not findings): runs end to end on live data. H-B6 became computable for five near-ceiling models (reasoning models + Haiku, a_m 0.93–1.00) but on only 3 shared problems, so its 0.000 is an artefact of incomplete data. Design note for the final analysis: the only matched cluster may be the near-ceiling one, where heterogeneous and homogeneous votes both score ≈ 1, so H-B6 is likely to be ≈ 0 for ceiling reasons — report that caveat with the result.
- **Next action:** top block.

### 2026-09-25 · Session 12 · Claude (Cowork, scheduled check-in) · Steady state; completion estimate
- **Observed (13:14 local):** runner restarted 09:07 with the Session 11 pacing (pid 5184) and has run cleanly since; 4,900 / 6,460 cells; no *.failed.json (73 *.attempts.json = retry bookkeeping). Groq OTPM errors for qwen stopped. Parked for today on their free daily caps: gemini_flash_lite (868 calls today), gptoss_120b (926; Groq TPD), gptoss_20b (631; Groq TPD), qwen38_27b + its temperature copies (1,000/1,000 requests, Groq RPD). nemotron_super still sees ~400 429/503 retries per hour at rpm 10 but completes cells (94 left); left as is. Every Ollama model and ministral_8b is complete; ollama_llama31_8b's last 13 cells are LLM-counterpart (c1) cells waiting on nemotron.
- **Remaining work ≈ calls:** gemini_flash_lite ~3,400 · gptoss_20b ~3,150 · qwen38_27b ~3,000 · gptoss_120b ~2,700 · nemotron_super ~1,900. At today's daily throughput that is ≈ 3–5 more days (gptoss_20b and gemini are the long poles) → **expected completion ≈ 2026-09-30**, all on free tiers. The NVIDIA route for gptoss_20b (PARKING_LOT) would save ~2 days; not adopted — the delay costs nothing.
- **Minor:** the test suite (mock models) writes to the real results/_runner/provider_errors.log and results/_quota/ (entries for llama-3.1-8b-instant / mock-*). Harmless (mock names, no real calls); ignore those lines when reading the error log.
- **Interim scorecard** (not findings): unchanged from Session 11.
- **Next action:** top block.

### 2026-09-25 · Session 12b · Claude (Cowork, user-requested overview) · NVIDIA 404 for nemotron_super
- **Observed (17:30 local):** 4,992 / 6,460 cells. Since 14:00 NVIDIA has answered some nemotron_super calls with an empty HTTP 404; from ~17:00 every call. The runner parked nemotron_super as a "config error" at 17:29 and exited with code 2 (every remaining model is parked; daily quotas reset tomorrow). 5 nemotron cells hit the failure cap (*.failed.json: 4 after 503s, 1 after 404). The c1_counterpart robustness job also depends on nemotron_super as the counterpart.
- **Likely causes (unverified):** the model was withdrawn/renamed on NVIDIA's free endpoint, or the free-tier allowance on the NVIDIA account is used up. The empty 404 differs from the earlier "Function … Not found" 404 seen for llama-3.1-nemotron-70b.
- **Next action for the next agent:** once more (after the date rolls over) try one nemotron call via REQUEST_PHASE0 (discover_models shows whether the model is still listed). If it is gone: pick a replacement counterpart/roster slot only via a DEVIATIONS.md entry — nemotron's completed cells stay, and its missing cells count against the >20% exclusion rule. Never add billing. NEEDS ADI (optional): check the NVIDIA account's free-credit status at build.nvidia.com.

### 2026-09-25 · Session 13 · Claude (Cowork, scheduled check-in) · Nemotron back; failed cells re-queued
- **Observed (19:17 local, 02:17 UTC):** 5,013 / 6,460. The local date has not rolled over yet, so the daily-quota models (gemini_flash_lite, gptoss_120b, gptoss_20b, qwen38_27b + copies) are still parked as designed; they resume on the first service tick after local midnight. nemotron_super's HTTP 404 was transient: a new runner (pid 26472, 18:22) is running its Phase A cells again, still with frequent 429s.
- **Done:** 14 nemotron_super *.failed.json (all transient provider errors: 7× empty 404 during the outage, 4× 429, 3× 503; no code or parse errors) moved to results/_runner/cleared_failed/ (same sub-paths) and nemotron's *.attempts.json moved to results/_runner/cleared_attempts/ (suffix .2), so the runner retries those cells. No result files touched. Session 12b's NVIDIA-credit concern is withdrawn for now.
- **Estimate:** unchanged, ≈ 2026-09-30.
- **Next action:** top block.

### 2026-09-26 · Session 14 · Claude (Cowork, scheduled check-in) · Day 2 of quota-paced running
- **Observed (02:18 local):** 5,298 / 6,460. After local midnight the runner (pid 24548, 00:07) resumed all parked models; gptoss_20b, gptoss_120b and gemini_flash_lite are parked again for today, qwen38_27b is running (464/1,000 requests). No *.failed.json. nemotron_super is **complete**, including the 14 re-queued cells, and the c1_counterpart cells for ollama_llama31_8b are done.
- **Note on Groq TPD:** Groq's 200k tokens-per-day cap is a rolling window, not a midnight reset (gptoss_20b re-hit it after 13 requests at 00:23). No change needed: parking lives only in a runner process's memory, and every new runner (each 15-min tick after the previous one exits with code 2) tries parked models again, so capacity is picked up as the window frees.
- **Remaining ≈ calls:** gemini_flash_lite ~2,900 (≈ 500 requests/day on the free tier → ~6 days, the long pole) · gptoss_20b ~2,800 (~4–5 days) · qwen38_27b ~2,600 plus 240 temperature-copy calls (~3 days) · gptoss_120b ~2,500 (~3 days). **Revised completion estimate ≈ 2026-10-02** (was 09-30). All free tier.
- **Next action:** top block.

### 2026-09-26 · Session 15 · Claude (Cowork, scheduled check-in) · Steady
- **Observed (10:22 local):** 5,437 / 6,460 (+139 since Session 14). No *.failed.json. qwen38_27b running (887/1,000 requests today); gptoss_20b (311 requests), gptoss_120b (527) and gemini_flash_lite (547) parked on their daily caps. Gemini hits its free quota at ≈ 500 requests/day (reset at local midnight); each 15-min runner re-tries it once, costing one request, which is harmless. Gemini also returns occasional 503 "model overloaded" (retried successfully).
- **Remaining cells:** gemini_flash_lite 326 (incl. all Phase A and 69 c1_counterpart cells) · gptoss_20b 254 · qwen38_27b 221 (+12 temperature cells) · gptoss_120b 210. Estimate unchanged: **≈ 2026-10-02**, gemini last.
- **Next action:** top block.

### 2026-09-26 · Session 16 · Claude (Cowork, scheduled check-in) · Day 2 closed
- **Observed (19:22 local):** 5,514 / 6,460 (+77 since Session 15, +501 over local 26 Sep). All four remaining models parked for the rest of the day on their free caps (requests today: qwen 1,000/1,000, gptoss_120b 812, gptoss_20b 593, gemini 592); they resume after local midnight. No *.failed.json; runner exits cleanly with code 2 each tick.
- **Remaining cells:** gemini_flash_lite 323 · qwen38_27b 220 (+12 temperature) · gptoss_20b 218 · gptoss_120b 173. Gemini's remaining work is mostly call-heavy Phase A and c1 cells (~2,900 calls at ~500/day). **Estimate ≈ 2026-10-02/03**, gemini last; the others ≈ 09-29/30.
- **Next action:** top block.

### 2026-09-27 · Session 17 · Claude (Cowork, scheduled check-in) · Day 3 caps reached early
- **Observed (05:24 local):** 5,824 / 6,460 (+310 since Session 16). All four remaining models already parked for local 27 Sep (requests today: gemini 519, qwen 640, gptoss_120b 189, gptoss_20b 168 — Groq's rolling token windows had only partly refilled). No *.failed.json; runner exits cleanly (code 2).
- **Remaining cells:** gemini_flash_lite 241 · gptoss_20b 146 · qwen38_27b 119 (+12 temperature) · gptoss_120b 118. Pace ≈ 300 cells/day → **estimate ≈ 2026-09-30 to 10-01**, gemini last (improved from 10-02/03).
- **Next action:** top block.

### 2026-09-27 · Session 18 · Claude (Cowork, scheduled check-in) · Steady
- **Observed (15:24 local):** 5,906 / 6,460 (+82 since Session 17; Groq's rolling token windows refill slowly through the day). All four remaining models parked; no *.failed.json; runner exits cleanly (code 2) each tick; autosync current.
- **Remaining cells:** gemini_flash_lite 237 · gptoss_20b 122 · qwen38_27b 109 (+12 temperature) · gptoss_120b 74. **Estimate ≈ 2026-09-30 to 10-01**, gemini last.
- **Next action:** top block.

### 2026-09-28 · Session 19 · Claude (Cowork, owner request) · Phase C "commons in the dark" designed, piloted, pre-registered
- **Goal:** the owner asked for a new experiment. Keep agents in a black box and watch whether they act selfishly, understand the resource's limits, and save for others; then reveal information step by step. (T3 collapsed under every instruction, so it could not say why agents drain a commons.)
- **Design (DECISIONS #20; prereg/PREREG_C.md):**
  - Same 4-agent regenerating source in every arm; only the agents' information differs.
  - Ladder C0 black box → C1 source visible → C2 rules → C3 others exist → C4 transparency → C5 talk.
  - Four extensions on C4: greedy1/greedy2 (scripted grabbers), need (agent A needs 2×), id_copies / id_humans (who the others are), known_end.
  - Probe controls C0_noprobe / C4_noprobe.
  - Each decision also states SAFE_TOTAL, the agent's own estimate of the sustainable take; this measures "knowing overreach".
  - 64 cells per model (≤ 2,400 calls); all 12 models; priority 4 (after Phase A/B).
- **Pilots** (1 seed per arm, ollama_llama31_8b + haiku45; p1_/p2_ cells, never analysed): invalid rate 0%.
  - Pilot 1 (permanent exhaustion): Llama emptied the source in round 1 in 10 of 14 arms. Regrowth changed to doubling + 5 with no permanent end.
  - Pilot 2: every crashed group (24 of 28 cells) stayed trapped near 5 units and none recovered. Primary metrics therefore became round-1 take (r1_overharvest) and mean source level (mean_stock).
- **Leads from the pilots** (not findings, one seed):
  - In the black box both models took very little (Haiku 1–5 units, well under a fair share). Once they saw the rules but believed they were alone, they took 4–8× the sustainable amount in round 1.
  - Agents often state a safe limit and then exceed their share of it (knowing overreach 0.68–0.95 at C3–C4).
  - With talk, Haiku agents coordinated on "15–20 each": friendly, but above the sustainable 13.
- **Code:** civlab/everyday/c_commons.py, experiments/v2/c_dark_commons.py, analysis/phase_c.py (tested on pilot-derived synthetic data), tests/test_phase_c.py (9 tests); full suite 42/42. queue_phase_c.yaml holds the full job, to be activated after PREREG_C is pushed.
- **Next action:** top block (activate Phase C once PREREG_C is on origin/main).
- **Addendum (activation):** PREREG_C.md is in commit 611852f (2026-09-27 20:09 -0700), an ancestor of origin/main; code files unchanged since that commit. Phase C job appended to queue.yaml (priority 4, models all) and RESTART set; Haiku Phase C started in the cloud workspace.

### 2026-09-28 · Session 20 · Claude (Cowork, scheduled) · Phase C running: Haiku complete
- **Haiku:** the Phase C cloud runner had died when the session idled (8/64 cells); restarted. It finished 07:09 UTC with 64/64 cells, no failures. Synced via results/_runner/haiku45_phasec_0711.tgz (64 files verified in the repo). Haiku's 28 pilot cells were synced too, for the record only (haiku45_phasec_pilot_0712.tgz; never analysed).
- **PC (00:15 local):** Phase C complete for ministral_8b, ollama_llama2_7b, ollama_llama31_8b, ollama_llama32_3b. In progress: nemotron_super 30/64, ollama_llama3_8b 33/64. Not started (behind Phase A/B on their daily caps): gemini_flash_lite, gptoss_20b/120b, qwen38_27b, ollama_qwen25_7b. No *.failed.json.
- **Interim** (`analysis.phase_c --interim`, 7 models, not findings):
  - Only H-C6 (knowing overreach, ≈ 0.6–0.7 at C3–C4) passes Holm so far. H-C2 and H-C3 point the predicted way (Holm p ≈ 0.055).
  - Black box C0: mean stock ≈ 91. Once the source level is visible (C1): ≈ 18.
  - H-C7 is not testable yet: no known_end or C4 group reaches round 10 with ≥ 48 units.
- **Next action:** top block. Run `analysis.phase_c` (confirmatory) only when all 12 models have finished Phase C.

### 2026-09-28 · Session 21 · Claude (Cowork, scheduled check-in) · Runner bug: parked models never resumed inside a long process
- **Observed (01:28 local):** Phase A/B at 5,932 / 6,460 (+26 since Session 18). The runner started at 21:07 was still running at 01:28, kept alive by slow nemotron Phase C cells. Its parked list still said "2026-09-27", so gemini_flash_lite, gptoss_20b/120b and qwen38_27b did not resume after midnight. Cause: run_queue computed `today` once at process start, and a worker never revisits cells it skipped earlier in the same process.
- **Fix (tools/run_queue.py; harness only, no experiment or analysis change):**
  - `today` is re-read before every cell.
  - A process now stops taking new cells after 2 h (MAX_RUNTIME_S), so the 15-minute service restarts it with fresh quotas and retries skipped cells.
  - tests/test_runner.py 5/5. RESTART set so the fix takes effect now.
- **Phase C:** done for ministral_8b, ollama_llama2_7b/llama3_8b/llama31_8b/llama32_3b/qwen25_7b and haiku45 (7 models). nemotron_super 38/64. The four quota-paced cloud models haven't started (priority 4, after their Phase A/B). No *.failed.json.
- **Remaining Phase A/B cells:** gemini 235 · gptoss_20b 117 · qwen38_27b 109 (+12) · gptoss_120b 55. Roughly a day lost to the bug. **Estimate ≈ 2026-10-01/02** for Phase A/B; Phase C cloud models follow (≈ 2–4 more days, gemini last).
- **Next action:** top block.
- **Session 21 addendum (03:31 local):** the fix works. A new runner (pid 13160, started 01:52) resumed the quota models on the new date: gemini_flash_lite 235 → 142 remaining (then parked for 28 Sep at 02:42); gptoss_20b/120b re-parked on Groq's rolling token window; qwen38_27b is running. Phase A/B 6,041 / 6,460. Phase C: nemotron_super 52/64; the four quota models haven't started. No *.failed.json. No "max runtime" exit yet (the process was < 2 h old).

### 2026-09-28 · Session 22 · Claude (Cowork, scheduled check-in) · Revised timeline: call-heavy tail
- **Observed (13:25 local):** Phase A/B 6,069 / 6,460. All four quota models parked for 28 Sep (Groq TPD 200k reached for qwen at 911 requests, gpt-oss-120b 426, gpt-oss-20b 409; gemini 546). Runner recycling works (one "max runtime" exit; clean code-2 exits otherwise). No *.failed.json. **Phase C complete for 8 models** (nemotron_super finished) · the 4 quota models 0/64 each.
- **Why the tail is slow:** the remaining cells are the call-heavy ones: Phase A (a4 reputation ≈ 50 calls/cell, a2 ≈ 25, a1 ≈ 20), c1_counterpart, and then Phase C (≈ 2,400 calls per model). Remaining calls, estimated from completed models:

  | Model | Phase A/B | Phase C | Pace |
  |---|---|---|---|
  | gemini | ≈ 1,930 | ≈ 2,400 | ≈ 550 req/day |
  | gpt-oss-20b | ≈ 1,600 | ≈ 2,400 | ≈ 400/day (token cap) |
  | gpt-oss-120b | ≈ 1,300 | ≈ 2,400 | ≈ 420/day |
  | qwen | ≈ 990 (+200 temperature) | ≈ 2,400 | ≈ 900/day |

- **Revised estimates:** Phase A/B complete ≈ 2026-10-02/03 (gemini and gpt-oss-20b last). Phase C for the four cloud models ≈ 2026-10-08/09. Earlier estimates (09-30 to 10-01) undercounted calls per remaining cell.
- **Option for Adi (not adopted; changing Phase C's model set would be a deviation):** analyse Phase C confirmatorily on the 8 finished models and report the 4 cloud models as a later robustness addendum. Default is to wait for all 12 as registered.
- **Next action:** top block.

### 2026-09-28 · Session 23 · Claude (Cowork, owner request) · Phase C confirmatory analysis (8 models)
- **Decision:** Adi approved analysing Phase C now on the 8 finished models, with the 4 cloud models as a later addendum. Logged as prereg/DEVIATIONS.md #1, including the disclosure that 7-model interim summaries had been seen.
- **Bug found and fixed first:** the pilot filter missed "p2_" cells (DECISIONS #21).
- **Confirmatory run:** `python3 -m analysis.phase_c --B 5000` → results/v2/_phase_c.md/.json. All 8 models valid (64/64 cells, invalid ≤ 0.4%). A rerun in the VM gives identical tables.
- **Independent verification:** analysis/verify_phase_c.py (no shared code) re-derives C2−C0 +2.917, C3−C2 −1.330, C5−C4 +6.283, knowing overreach 0.736, needy share 0.438, mean stock C0 92.35 / C1 17.32. All match (results/v2/_phase_c_verification.txt).
- **Results** (Holm across H-C1–H-C7; secondary X1–X7 Holm, exploratory):
  - **H-C6 SUPPORTED.** At C3–C4, agents request more than their own stated safe share in 74% of decisions (+0.637 above the 10% threshold, CI [+0.50, +0.76]). Holds in all 8 models and every robustness variant.
  - **H-C3 SUPPORTED.** Learning that others share the source cuts the round-1 take (−1.33 × sustainable share, Holm p = 0.028; 7/8 models). Not robust to every exclusion (it loses significance without the pilot models or without Haiku).
  - **H-C2 not supported after Holm.** Knowing the rules while believing you're alone raises the round-1 take by +2.92 × (CI [+0.73, +4.46]; p = 0.018; Holm 0.072; 7/8 models).
  - **H-C1 not supported.** The black-box round-1 take is not distinguishable from the sustainable share on average (+0.18). But 7 of 8 models asked 0–6 units, while Llama 3.1 8B asked ~100. Without Meta models or without the pilot models it becomes significantly below the sustainable share.
  - **H-C4 not supported.** Transparency: +1.4 stock, CI spans 0.
  - **H-C5 not supported after Holm.** Talk: +6.3 stock (p = 0.05, Holm 0.15). Driven by Haiku (+16), Nemotron (+26) and Ministral (+9); the small local models crash in round 1 whatever happens.
  - **H-C7 not testable.** No group reached round 10 with ≥ 48 units.
  - **Secondary:**
    - X3 (needy agent's share 0.44 > 0.25) survives, but mostly because the needy agent asked for more (round 1: 57 vs 34 in C4); the others eased off only slightly (29 vs 34).
    - X2 (two greedy agents vs one): +3.5 stock, not after Holm.
    - Identity framing (X4/X5): no effect.
    - Probe controls (X6/X7): no effect, so asking about limits did not measurably change behaviour.
  - **Descriptive:** black-box mean stock 92 vs 17 once the level is visible (C1). Of 447 crashed groups, 9 recovered (2%). Spontaneous mentions of other agents in C0–C2 ≈ 1% of decisions (none were mentioned to them).
- **Next action:** top block. Phase C addendum when the 4 cloud models finish.

### 2026-09-28 · Session 24 · Claude (Cowork, scheduled check-in) · Quiet evening
- **Observed (23:38 local, still 28 Sep):** Phase A/B 6,082 / 6,460 (+13; all four quota models were parked for the rest of the local day, as expected). Runner exits cleanly (code 2) every tick; no *.failed.json. Phase C: the 4 cloud models 0/64 (they start after their A/B cells).
- **Remaining A/B cells:** gemini 141 · gptoss_20b 103 · qwen38_27b 88 (+10) · gptoss_120b 36. Estimates unchanged (A/B ≈ 10-02/03; Phase C cloud addendum ≈ 10-08/09).
- **Next action:** top block.

### 2026-09-29 · Session 25 · Claude (Cowork, scheduled check-in) · Day on the free caps
- **Observed (09:40 local):** Phase A/B 6,145 / 6,460 (+63 today, before the caps hit). All four quota models were parked for 29 Sep by 09:40 (Groq TPD / Gemini RPD). Recycling works; no *.failed.json. Phase C cloud models 0/64.
- **Remaining A/B cells:** gemini 109 · gptoss_20b 95 · qwen38_27b 72 (+10 temperature) · gptoss_120b 29. The gpt-oss models finish only ≈ 8–10 cells/day because what's left is a4_reputation (≈ 50 calls/cell) and c1. **Estimates:** A/B ≈ 10-03; Phase C cloud addendum ≈ 10-09/10.
- **Speed-up option (needs Adi; would be a logged deviation):** NVIDIA NIM's free tier also serves openai/gpt-oss-20b and -120b, and NVIDIA capacity is idle now that nemotron is done. Routing the two gpt-oss models there (same open weights, different host) could save about 3–4 days. Not adopted.
- **Next action:** top block.

### 2026-09-29 · Session 26 · Claude (Cowork, owner request) · gpt-oss fallback to NVIDIA
- **Decision:** Adi approved serving gpt-oss through NVIDIA's free tier as well (prereg/DEVIATIONS.md #2).
- **Built:** a router fallback. Groq stays primary; once its daily cap is hit, the same weights on NVIDIA are used for the rest of the local day. Same model id, temperature, reasoning_effort=low and prompts, with the strict served-model check. Every call record carries its `provider`. DECISIONS #22; tests/test_fallback.py; suite 45/45. RESTART set.
- **First run (15:37 local):**
  - **gptoss_20b:** works. Groq was capped, so the next 40 calls were served by nvidia/openai/gpt-oss-20b with no errors.
  - **gptoss_120b:** NVIDIA answered HTTP 410 ("reached its end of life on 2026-09-03"). Its fallback was removed and it stays Groq-only (DEVIATIONS #2a). The two cells that hit the 410 left no results; their retry counters were moved to results/_runner/cleared_attempts/ (*.410.json).
- **Expected effect:** gptoss_20b is no longer bound by the 200k tokens/day cap; ≈ 1,300 A/B calls + ≈ 2,400 Phase C calls could finish in about 1–2 days. The long poles are now gemini (≈ 500 req/day) and gptoss_120b (Groq only) for A/B around 10-02/03; Phase C cloud addendum for gemini/120b ≈ 10-08/09 (qwen and gpt-oss-20b sooner).
- **Write-up note:** gpt-oss-20b results need the robustness check "cells with any NVIDIA-served call excluded" (DEVIATIONS #2).
- **Next action:** top block.

### 2026-09-29 · Session 27 · Claude (Cowork, scheduled check-in) · gpt-oss-20b done via NVIDIA fallback
- **Observed (19:38 local):** Phase A/B 6,252 / 6,460 (+107 since Session 25). **gptoss_20b finished everything**, Phase A/B and Phase C 64/64, within about 4 hours of the fallback going live. NVIDIA errors were minor: 5 ReadTimeouts, all retried. Runner recycling works (2 "max runtime" exits). No *.failed.json.
- **Host mix for gptoss_20b (for the DEVIATIONS #2 robustness check):**
  - All Phase B everyday tasks (T1–T5, T4b) are 100% Groq.
  - a2_pricing, a3_panel and a6_commons are Groq-only (a2: 5 NVIDIA calls).
  - a1_ipd 63%, a4_reputation 77%, a5_naming 95% and c1_counterpart 96% of calls came from NVIDIA.
  - Phase C: 2,541 NVIDIA vs 30 Groq calls.
- **Remaining A/B:** gemini 109 · qwen38_27b 67 (+10 temperature) · gptoss_120b 22 (Groq only). Phase C: gemini, qwen and gptoss_120b 0/64.
- **Estimates:** A/B ≈ 10-02/03 (gemini last). Phase C cloud addendum ≈ 10-08 (gemini ≈ 5 days of quota after A/B; qwen and 120b sooner).
- **Next action:** top block.

### 2026-09-29 · Session 28 · Claude (Cowork, owner question) · Interim look (not findings)
- **Progress (21:22 local):** A/B 6,253 / 6,460. Interim everyday_effects (12 models where available): H-B4, H-B7, H-B9 and H-B10 still survive Holm. H-B3 (recent reputation) at p = 0.052 (unadjusted), up from 0.10.
- **New exclusions from reasoning models on T4b answer-only:** gptoss_20b, gptoss_120b and qwen38_27b each have ≈ 28% invalid actions (> 10%), so they are excluded from H-B9 per PREREG_B §7. They likely spend the max_tokens budget reasoning before answering. Caveat for the write-up: the answer-only control does not apply cleanly to reasoning models.
- **Descriptive:**
  - Manipulative-customer refunds under H3 are 0–0.1 for all four reasoning models vs 0.6–1.0 for the other eight.
  - In T2, all 12 models pick the betraying worker more often with the self-report panel than with the lifetime panel. The recent-window panel (game) lowers betrayer picks in all 12, but the accuracy gain stays small.
  - Phase C, gptoss_20b (mostly NVIDIA-served): cautious in the black box (0.7 units in round 1). Once the level is visible it takes ≈ 40–70 units in round 1 and crashes the source in round 1 in every arm, talk included.

### 2026-09-30 · Session 29 · Claude (Cowork, scheduled check-in) · Qwen done with A/B
- **Observed (05:40 local):** Phase A/B 6,352 / 6,460 (+100 since Session 27). **qwen38_27b and its temperature copies have finished Phase A/B**; qwen started Phase C (4/64). Remaining A/B: gemini 91 · gptoss_120b 17 (Groq only). All three quota models are parked for 30 Sep. No *.failed.json.
- **Estimates:** A/B complete ≈ 10-02 (gemini last), then the Phase B/A confirmatory analysis and the verification pass. Phase C cloud addendum: qwen ≈ 10-03, gemini ≈ 10-07, gptoss_120b ≈ 10-08.
- **Next action:** top block.

### 2026-09-30 · Session 30 · Claude (Cowork, scheduled check-in) · Gemini is the last A/B model
- **Observed (15:39 local):** Phase A/B 6,359 / 6,460. gptoss_120b has 10 A/B cells left (Groq). Gemini has 91: a1 8, a2 1, a4 12, a5 1 and 69 c1_counterpart cells, ≈ 1,100 calls at ≈ 550–600 requests/day, with 503 retries counted. Phase C: qwen 12/64 (its Groq token cap binds on the longer Phase C prompts); gemini and 120b 0/64. All three parked for 30 Sep; no *.failed.json.
- **Revised estimates:** A/B complete ≈ 10-03 (gemini c1 cells last), then the confirmatory analysis and the verification pass. Phase C addendum: qwen ≈ 10-04, gptoss_120b ≈ 10-08, gemini ≈ 10-08/09.
- **Next action:** top block.
