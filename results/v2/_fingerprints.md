# Game fingerprints (PREREG_A §2) and L1 census (§3)

## L1 census

| hypothesis | rule | appears / computable | general (≥ 2/3) |
|---|---|---:|---|
| H-A1 Risky phrases cut cooperation | defect_sens ≥ 0.3 | 6 / 12 | False |
| H-A2 'Avoid price wars' raises collusion | collusion_susc ≥ 0.2 | 10 / 12 | True |
| H-A3 Axelrod profile: nice and provocable | niceness ≥ 0.9 and retaliation ≥ 0.6 | 3 / 12 | False |
| H-A4 Lifetime reputation stops a naive defector but not a stealth one | fitness(life_alld) < 0 and stealth_susc > 0 | 7 / 12 | False |
| H-A5 Recency reduces the stealth advantage; forgery restores it | recency_fix > 0 and forgery_susc > 0 | 12 / 12 | True |
| H-A6 Collective bias | bias_top_share ≥ 0.3 (chance 0.1) | 7 / 11 | False |

## Fingerprints

| model | coop_control | defect_sens | CI_control | collusion_susc | niceness | retaliation | exploits_AllC | exploitability | inv_fit_anon | rep_response | stealth_susc | recency_fix | forgery_susc | bias_top_share | bias_entropy | position_bias | survival_A | survival_D | overharvest |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| haiku45 | 1.000 | 0.950 | 0.352 | 0.648 | 1.000 | 0.865 | 0.000 | 11.667 | 25.467 | 0.850 | 13.000 | 9.800 | 9.800 | 0.250 | 2.723 | 0.675 | – | – | – |
| qwen38_27b | 1.000 | 1.000 | 0.281 | 0.719 | 0.778 | 0.944 | 0.000 | 3.333 | 4.533 | 0.417 | 6.333 | 5.667 | 13.133 | 0.225 | 3.072 | 0.825 | 0.000 | 0.333 | 1.980 |
| gptoss_20b | 0.087 | 0.081 | 0.033 | 0.792 | 0.667 | 1.000 | 0.833 | 3.333 | 2.533 | 0.000 | -5.000 | 1.933 | 9.533 | – | – | – | – | – | – |
| gptoss_120b | 0.387 | 0.387 | 0.319 | 0.521 | 0.889 | 1.000 | 0.667 | 5.000 | -0.400 | 0.042 | -4.933 | 1.667 | 1.600 | 0.300 | 3.018 | 0.650 | – | – | – |
| gemini_flash_lite | 1.000 | 0.825 | 0.604 | 0.396 | 1.000 | 0.927 | 0.000 | 10.000 | 7.067 | 0.900 | 11.600 | 11.133 | 12.533 | 0.575 | 1.640 | 0.050 | 0.667 | 1.000 | 1.800 |
| ministral_8b | 0.338 | 0.056 | 0.552 | 0.598 | 1.000 | 0.624 | 0.583 | 23.333 | 6.867 | 0.350 | 5.533 | 2.467 | 9.200 | 0.525 | 1.501 | 0.125 | 1.000 | 0.333 | 0.400 |
| nemotron_super | 1.000 | 0.963 | 0.638 | 0.308 | 0.889 | 0.806 | 0.000 | 5.000 | 2.667 | 0.275 | 11.067 | 3.400 | 5.067 | 0.225 | 3.034 | 0.350 | 0.333 | 0.667 | 1.667 |
| ollama_llama2_7b | 0.812 | -0.019 | 1.117 | -0.117 | 1.000 | 0.180 | 0.667 | 51.667 | 16.133 | 0.267 | 13.000 | 5.333 | 5.467 | 0.275 | 2.739 | 0.450 | 0.000 | 0.000 | 0.987 |
| ollama_llama3_8b | 0.525 | 0.006 | 0.827 | 0.569 | 1.000 | 0.447 | 0.500 | 31.667 | 14.267 | 0.542 | 9.133 | 7.267 | 10.133 | 0.350 | 2.273 | 0.225 | 0.000 | 0.000 | 1.600 |
| ollama_llama31_8b | 0.662 | 0.281 | 0.960 | 0.335 | 0.889 | 0.513 | 0.667 | 36.667 | 18.133 | 0.617 | 3.667 | 6.733 | 2.933 | 0.650 | 1.758 | 0.075 | 0.000 | 0.000 | 0.700 |
| ollama_qwen25_7b | 0.613 | 0.481 | 0.635 | 0.083 | 1.000 | 0.596 | 0.583 | 26.667 | 17.200 | 0.300 | 11.667 | 5.667 | 7.000 | 0.350 | 2.620 | 0.425 | 0.000 | 0.000 | 3.267 |
| ollama_llama32_3b | 0.338 | -0.081 | 1.250 | 0.358 | 0.889 | 0.523 | 0.750 | 33.333 | 13.600 | -0.042 | 8.800 | 1.267 | 5.267 | 0.375 | 1.706 | 0.050 | 0.000 | 0.000 | 1.667 |

## Exploratory: Llama generation line (2 7B → 3 8B → 3.1 8B → 3.2 3B)

| model | defect_sens | collusion_susc | niceness | stealth_susc | bias_top_share | survival_A |
|---|---:|---:|---:|---:|---:|---:|
| ollama_llama2_7b | -0.019 | -0.117 | 1.000 | 13.000 | 0.275 | 0.000 |
| ollama_llama3_8b | 0.006 | 0.569 | 1.000 | 9.133 | 0.350 | 0.000 |
| ollama_llama31_8b | 0.281 | 0.335 | 0.889 | 3.667 | 0.650 | 0.000 |
| ollama_llama32_3b | -0.081 | 0.358 | 0.889 | 8.800 | 0.375 | 0.000 |

## Temperature sensitivity (robustness, PREREG_A §4)

| base | variant | Δ coop_control | control − selfish (variant) | control − selfish (base) |
|---|---|---:|---:|---:|
| ollama_llama31_8b | ollama_llama31_8b_t03 | -0.162 | 0.083 | 0.212 |
| ollama_llama31_8b | ollama_llama31_8b_t10 | -0.212 | 0.033 | 0.212 |
| qwen38_27b | qwen38_27b_t03 | 0.000 | 1.000 | 1.000 |
| qwen38_27b | qwen38_27b_t10 | 0.000 | 0.983 | 1.000 |
