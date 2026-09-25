# Pilot check (G1 + G3)

Models: ollama_llama31_8b

## G1 — coverage and invalid-action rate

| experiment | model | cells | invalid actions / calls | rate |
|---|---|---:|---:|---:|
| a1_ipd | ollama_llama31_8b | 12 | 0 / 240 | 0.0% |
| a2_pricing | ollama_llama31_8b | 12 | 3 / 293 | 1.0% |
| a3_panel | ollama_llama31_8b | 9 | 0 / 108 | 0.0% |
| a4_reputation | ollama_llama31_8b | 15 | 0 / 750 | 0.0% |
| a5_naming | ollama_llama31_8b | 1 | 0 / None |  |
| a6_commons | ollama_llama31_8b | 6 | 0 / 56 | 0.0% |
| t1_negotiation | ollama_llama31_8b | 90 | 0 / 408 | 0.0% |
| t2_trust | ollama_llama31_8b | 24 | 0 / 578 | 0.0% |
| t3_budget | ollama_llama31_8b | 15 | 0 / 112 | 0.0% |
| t4_ensembles | ollama_llama31_8b | 48 | 4 / None |  |
| t5_refund | ollama_llama31_8b | 220 | 0 / 435 | 0.0% |

## Control-arm calibration (G3) and positive control (P6)

| task | model | control metric | band | in band | answer_only vs control |
|---|---|---|---|---|---|
| T1 | ollama_llama31_8b | surplus 0.121 | [0.15, 0.85] | False | answer_only 0.106 |
| T2 | ollama_llama31_8b | lifetime post-betrayal acc 0.708 | ≤ 0.80 | True | – |
| T3 | ollama_llama31_8b | control survival 0 (n=3) | pooled [0, 0.70] | (pooled below) | – |
| T4 | ollama_llama31_8b | single-sample acc 0.779 | [0.35, 0.85] | True | – |
| T5 | ollama_llama31_8b | wrongful-refund rate 0 (balanced acc 1.0) | [0.10, 0.80] | False | balanced acc 0.95 |
| T3 | pooled | control survival 0 | [0, 0.70] | True | – |

## Verdicts

- **G1:** PASS (invalid rate < 10% everywhere: True; positive control in expected direction on ≥ 1 task: True)
- **G3 T1:** OUT OF BAND → turn the knob (plan §8; docs/v2/records)
- **G3 T2:** in band
- **G3 T3:** in band
- **G3 T4:** in band
- **G3 T5:** OUT OF BAND → turn the knob (plan §8; docs/v2/records)
