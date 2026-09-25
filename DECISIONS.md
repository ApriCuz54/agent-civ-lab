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
