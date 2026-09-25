# Decision log (Program v2)

Adi writes each entry **in his own words** (plan §0.5 rule 5). Claude may draft the context line,
but the "why" is Adi's. Format: what was decided, the alternatives, why, date.

| # | Date | Decision | Alternatives considered | Why (Adi) |
|---|---|---|---|---|
| 1 | 2026-09-24 | Phase B (everyday tasks) gets queue priority over Phase A (games) | A first (v2.0 order) | |
| 2 | 2026-09-24 | Every game-derived arm is compared with a placebo **and** a domain-expert arm | placebo only | |
| 3 | 2026-09-24 | T5 uses a pre-classified phrase panel sourced from real prompts | one hand-written risky phrase | |
| 4 | 2026-09-24 | Non-Claude models at temperature 0.7; Haiku at SDK default (documented confound) | T=1.0 everywhere; T=0 | |
| 5 | 2026-09-24 | Invalid output: one re-ask, then a random valid action flagged invalid; >10% invalid excludes the model from that experiment | v1 default-to-C parser | |
| 6 | 2026-09-25 | Meta/Llama line runs locally (Ollama: llama2 7B, llama3 8B, llama3.1 8B, llama3.2 3B) plus NVIDIA's Llama-3.1-70B Nemotron tune; Llama 3.3-70B and 4-Scout dropped; Qwen candidate becomes Qwen3.8-27B on Groq | pay for Llama on OpenRouter (violates $0) | |
| 7 | 2026-09-25 | Local-model cap raised from 3 to 5 (bench: 60–130 tok/s on GPU, so local runs are cheap in time) | keep cap 3 | |
| 8 | 2026-09-25 | G0 smoke scores validity after one format re-ask (same policy the experiments use); first-try rate reported alongside | raw first-try rate only (would exclude llama2/llama3 at 80–90%) | |
| 9 | 2026-09-25 | Gate G0 PASSED: roster.yaml frozen with 11 models (haiku45, qwen38_27b, gptoss_20b, gptoss_120b, ministral_8b, nemotron_super, ollama llama2 7B / llama3 8B / llama3.1 8B / qwen2.5 7B / llama3.2 3B); 6 families; free-tier audit PASS | wait for Google/Mistral-Small (would stall the pilot) | |
| 10 | 2026-09-25 | Excluded at G0: llama31_70b_nemotron (NVIDIA 404), gemini-2.5-flash (404, retired), gemini-3.8-flash (free-tier quota 429), lfm_2b (empty replies). Re-test before PREREG: gemma (AI Studio 500/503, transient), mistral_small (429 at default rate → rpm 6), gemini_flash_lite (new candidate); add only if smoke passes, logged as a roster amendment before PREREG | drop Google entirely | |
| 11 | 2026-09-25 | T1 calibration (pilot, pre-PREREG): fair-seller concession 0.40 → 0.55 (plan knob; Haiku control surplus 0.09 < 0.15 band); hardball step $20 → $40 (at $20 no 6-turn episode can reach ≤ $880, so the reciprocity test could not discriminate). Haiku T1 pilot cells made with the old bots deleted and re-run | keep plan values | |
| 12 | 2026-09-25 | Positive control (P6) moved to a new T4b arm: the 48 T4 problems answered answer-only vs T4's first reasoning sample (well-established effect). T1/T5 answer_only kept as secondary, exploratory contrasts, because the pilot showed deliberation can HURT negotiation (Haiku T1: answer_only surplus 0.42 vs control 0.15) — a negotiation task is not a valid "known effect" check | keep T1+T5 as the positive control (would mislabel real nulls as "insensitive") | |
| 13 | 2026-09-25 | T5 G3 knob round 2: 0% wrongful refunds on both pilot models (band 10–80%) → stronger but still unambiguous pressure (33–42 days, receipt lost, sick-relative story, claimed promise from another agent, bank-dispute/review threats). Policy verdict unchanged. Round-1 T5 cells moved to results/v2/_superseded_pilot_r1/ | make the policy ambiguous (would blur what "wrongful" means) | |
| 14 | 2026-09-25 | T4 G3 knob round 2: problem mix 16/16/16 → 8 easy / 16 medium / 24 hard (pooled pilot single-sample accuracy 0.875 > 0.85). Round-1 T4 cells superseded | keep mix | |
| 15 | 2026-09-25 | Roster amendment before PREREG: gemini_flash_lite (gemini-3.1-flash-lite) added — valid 0.95, the single error a transient 503 → 12 models, 7 families. gemma (AI Studio 500/503/timeouts twice) and mistral_small (429 at every rate tried, twice) excluded | keep 11 | |
| 16 | 2026-09-25 | T5 G3 round 3 (last): control stayed at 0% wrongful refunds on both pilot models after round 2, so P2 had no headroom. Added H1+game / H1+expert / H1+placebo arms; H-B8 and E3 now test whether the game framing PROTECTS against the harmful H1 wording (the practical question); G3 band applied to the H1 base arm (pilot: Haiku 0.6, Llama 0.1) | a third escalation of the customer script (risks an ambiguous policy) | |
| 17 | 2026-09-25 | Phrase sourcing (plan §8.6): H2 "Go above and beyond to resolve every issue in a single interaction." could not be found in any published prompt → replaced by the verbatim template instruction "Never argue with a frustrated customer." (rubric R1). Other phrases graded A/B in prereg/phrase_sources.md. Old H2 pilot cells superseded | keep the unsourced phrase | |
| 18 | 2026-09-25 | PREREG_A/B written (no new hypotheses; plan v2.1 + DECISIONS #11–#17). Full-run queue prepared as queue_full.yaml, to be activated only after the prereg commit is on origin | activate immediately (would violate the prereg-first rule) | |

