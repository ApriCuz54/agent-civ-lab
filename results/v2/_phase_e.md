# Phase E confirmatory results

B = 5000, seed 20261101. Valid models: ollama_llama2_7b, ollama_llama3_8b, ollama_llama31_8b, ollama_llama32_3b, ollama_qwen25_7b, ministral_8b, nemotron_ultra.

| test | hypothesis | n | estimate | 95% CI | p | p (Holm) | survives | verdict |
|---|---|---|---|---|---|---|---|---|
| H-E1 | Identity + memory beats stateless | 7 | 0.005 | [-0.015, 0.026] | 0.6516 | 1.0000 | False | don't bother |
| H-E2 | Shadow-of-the-future instruction beats placebo | 7 | -0.005 | [-0.021, 0.009] | 0.4744 | 1.0000 | False | don't bother |
| H-E3 | Verified record beats self-reported record | 7 | 0.042 | [0.024, 0.062] | 0.0002 | 0.0014 | True | don't bother |
| H-E4 | Forgiveness rule beats placebo | 7 | -0.007 | [-0.023, 0.010] | 0.4072 | 1.0000 | False | don't bother |
| H-E4b | Forgiveness gains more against reciprocators than exploiters | 7 | -0.034 | [-0.070, 0.003] | 0.0760 | 0.4560 | False |  |
| H-E5 | Walk-away beats A1 against exploiters and travellers | 7 | 0.009 | [-0.015, 0.036] | 0.5168 | 1.0000 | False | don't bother |
| H-E6 | Stage 0 forgiveness predicts recovery in tasks (Spearman) | 7 | -0.071 |  | 0.9022 | 1.0000 | False |  |
| H-E5-noninf | Walk-away costs little against reciprocators | 7 | -0.024 | [-0.075, 0.022] | 0.3476 | nan | None |  |
