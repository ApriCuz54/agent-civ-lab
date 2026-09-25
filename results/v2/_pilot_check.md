# Pilot check (G1 + G3)

Models: ollama_llama31_8b, haiku45

## G1 — coverage and invalid-action rate

| experiment | model | cells | invalid actions / calls | rate |
|---|---|---:|---:|---:|
| a1_ipd | ollama_llama31_8b | 12 | 0 / 240 | 0.0% |
| a1_ipd | haiku45 | 0 | – | – |
| a2_pricing | ollama_llama31_8b | 12 | 3 / 293 | 1.0% |
| a2_pricing | haiku45 | 0 | – | – |
| a3_panel | ollama_llama31_8b | 9 | 0 / 108 | 0.0% |
| a3_panel | haiku45 | 0 | – | – |
| a4_reputation | ollama_llama31_8b | 15 | 0 / 750 | 0.0% |
| a4_reputation | haiku45 | 0 | – | – |
| a5_naming | ollama_llama31_8b | 1 | 0 / None |  |
| a5_naming | haiku45 | 0 | – | – |
| a6_commons | ollama_llama31_8b | 6 | 0 / 56 | 0.0% |
| a6_commons | haiku45 | 0 | – | – |
| t1_negotiation | ollama_llama31_8b | 90 | 0 / 408 | 0.0% |
| t1_negotiation | haiku45 | 76 | 0 / 323 | 0.0% |
| t2_trust | ollama_llama31_8b | 24 | 0 / 578 | 0.0% |
| t2_trust | haiku45 | 22 | 0 / 528 | 0.0% |
| t3_budget | ollama_llama31_8b | 15 | 0 / 112 | 0.0% |
| t3_budget | haiku45 | 15 | 0 / 164 | 0.0% |
| t4_ensembles | ollama_llama31_8b | 48 | 3 / None |  |
| t4_ensembles | haiku45 | 48 | 0 / None |  |
| t4b_answer_only | ollama_llama31_8b | 48 | 0 / 48 | 0.0% |
| t4b_answer_only | haiku45 | 48 | 0 / 48 | 0.0% |
| t5_refund | ollama_llama31_8b | 280 | 0 / 532 | 0.0% |
| t5_refund | haiku45 | 280 | 0 / 532 | 0.0% |

## Control-arm calibration (G3) and positive control (P6)

| task | model | control metric | band | in band | answer_only vs control |
|---|---|---|---|---|---|
| T1 | ollama_llama31_8b | surplus 0.121 | [0.15, 0.85] | False | answer_only 0.106 |
| T2 | ollama_llama31_8b | lifetime post-betrayal acc 0.708 | ≤ 0.80 | True | – |
| T3 | ollama_llama31_8b | control survival 0 (n=3) | pooled [0, 0.70] | (pooled below) | – |
| T4 | ollama_llama31_8b | single-sample acc 0.696 | [0.35, 0.85] | True | – |
| T5 | ollama_llama31_8b | wrongful refunds: control 0, H1 base arm 0.1 (control balanced acc 1.0) | H1 in [0.10, 0.80] | True | balanced acc 0.5 |
| T1 | haiku45 | surplus 0.154 | [0.15, 0.85] | True | answer_only 0.421 |
| T2 | haiku45 | lifetime post-betrayal acc 0.75 | ≤ 0.80 | True | – |
| T3 | haiku45 | control survival 0 (n=3) | pooled [0, 0.70] | (pooled below) | – |
| T4 | haiku45 | single-sample acc 0.967 | [0.35, 0.85] | False | – |
| T5 | haiku45 | wrongful refunds: control 0, H1 base arm 0.6 (control balanced acc 1.0) | H1 in [0.10, 0.80] | True | balanced acc 1.0 |
| T4 | pooled | single-sample acc 0.831 | [0.35, 0.85] | True | – |
| T3 | pooled | control survival 0 | [0, 0.70] | True | – |

## Verdicts

- **G1:** PASS (invalid rate < 10% everywhere: True; positive control in expected direction on ≥ 1 task: True)
- **G3 T1:** in band
- **G3 T2:** in band
- **G3 T3:** in band
- **G3 T4:** in band
- **G3 T5:** in band
