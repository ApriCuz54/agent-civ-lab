# Phase F exploratory results (no verdicts; PREREG_F §5)

From `python -m analysis.phase_f_explore` (B = 2000, seed 20261106). Pooled = mean over models of per-model means. CIs are hierarchical bootstrap, uncorrected; none of this is confirmatory.

## A. nemotron_ultra robustness set

- nemotron_ultra: 128 cells, invalid rate 0.0000, valid True

| comparison | nemotron estimate [95% CI] | primary pool, same rogues [95% CI] |
|---|---|---|
| H-F1: One rogue costs the fleet output (harm > 0, D0) | 0.218 [0.196, 0.242] | 0.145 [0.109, 0.178] |
| H-F3: Liar causes more harm than Selfish (D0) | 0.013 [-0.067, 0.089] | 0.057 [0.030, 0.086] |
| H-F4: Verified records cut harm (D1 vs D0) | 0.001 [-0.020, 0.023] | 0.035 [-0.002, 0.074] |
| H-F9: Shifter causes more harm than Liar under verified records (D1) | 0.003 [-0.049, 0.054] | 0.006 [-0.031, 0.041] |
| H-F10: Identity binding cuts the Shifter's harm (D6 vs D1) | -0.021 [-0.052, 0.008] | -0.020 [-0.071, 0.031] |
| D5-D0: Placebo vs baseline (instruction-length control) | 0.012 [-0.008, 0.032] | -0.004 [-0.037, 0.033] |
| D6-D0: Identity-bound record vs baseline | -0.007 [-0.033, 0.020] | 0.013 [-0.027, 0.049] |

**nemotron_ultra mean harm**

| rogue | D0 | D1 | D5 | D6 |
|---|---|---|---|---|
| selfish | 0.212 | 0.193 | 0.203 | 0.190 |
| liar | 0.224 | 0.229 | 0.235 | 0.231 |
| shifter | 0.217 | 0.232 | 0.249 | 0.211 |

**primary pool mean harm, same design**

| rogue | D0 | D1 | D5 | D6 |
|---|---|---|---|---|
| selfish | 0.112 | 0.172 | 0.118 | 0.139 |
| liar | 0.169 | 0.180 | 0.152 | 0.165 |
| shifter | 0.153 | 0.187 | 0.150 | 0.167 |

**nemotron_ultra share of cells where the rogue was detected**

| rogue | D0 | D1 | D5 | D6 |
|---|---|---|---|---|
| selfish | 1.00 | 0.75 | 0.75 | 0.75 |
| liar | 0.50 | 0.50 | 0.38 | 0.50 |
| shifter | 0.00 | 0.00 | 0.00 | 0.62 |

nemotron_ultra output without a rogue: D0 131.9, D1 133.0, D5 132.8, D6 132.6

## B. Primary models (6)

**Share of cells where most honest members flagged the rogue**

| rogue | D0 | D1 | D2 | D1D2 | D3 | D4 | D5 | D6 |
|---|---|---|---|---|---|---|---|---|
| selfish | 0.73 | 0.81 | 0.71 | 0.81 | 0.71 | 0.71 | 0.65 | 0.75 |
| liar | 0.08 | 0.48 | 0.17 | 0.62 | 0.12 | 0.21 | 0.08 | 0.42 |
| framer | 0.31 | 0.48 | 0.56 | 0.77 | 0.35 | 0.48 | 0.31 | 0.44 |
| shifter | 0.00 | 0.00 | 0.02 | 0.06 | 0.00 | 0.00 | 0.00 | 0.52 |

**Mean detection round (detected cells)**

| rogue | D0 | D1 | D2 | D1D2 | D3 | D4 | D5 | D6 |
|---|---|---|---|---|---|---|---|---|
| selfish | 7.2 | 7.0 | 7.1 | 6.5 | 6.9 | 6.2 | 7.2 | 6.5 |
| liar | 7.2 | 7.3 | 9.5 | 7.9 | 7.2 | 7.5 | 8.3 | 7.6 |
| framer | 6.9 | 7.1 | 7.8 | 7.8 | 6.2 | 6.7 | 6.5 | 6.7 |
| shifter | – | – | 4.0 | 8.0 | – | – | – | 7.9 |

**False-flag rate (honest flags naming an honest member, per decision)**

| rogue | D0 | D1 | D2 | D1D2 | D3 | D4 | D5 | D6 |
|---|---|---|---|---|---|---|---|---|
| none | 0.176 | 0.230 | 0.217 | 0.265 | 0.159 | 0.237 | 0.140 | 0.193 |
| selfish | 0.114 | 0.114 | 0.223 | 0.244 | 0.104 | 0.149 | 0.108 | 0.113 |
| liar | 0.172 | 0.176 | 0.206 | 0.252 | 0.180 | 0.235 | 0.167 | 0.167 |
| framer | 0.241 | 0.244 | 0.360 | 0.387 | 0.237 | 0.283 | 0.237 | 0.239 |
| shifter | 0.197 | 0.257 | 0.209 | 0.275 | 0.166 | 0.265 | 0.153 | 0.145 |

**Share of cells with an honest member removed**

| rogue | D2 | D1D2 |
|---|---|---|
| none | 0.27 | 0.31 |
| selfish | 0.35 | 0.40 |
| liar | 0.25 | 0.35 |
| framer | 0.67 | 0.67 |
| shifter | 0.19 | 0.21 |

**Share of cells with the rogue removed**

| rogue | D2 | D1D2 |
|---|---|---|
| selfish | 0.71 | 0.81 |
| liar | 0.19 | 0.65 |
| framer | 0.58 | 0.79 |
| shifter | 0.02 | 0.08 |

**Mean round the rogue was removed**

| rogue | D2 | D1D2 |
|---|---|---|
| selfish | 7.1 | 6.5 |
| liar | 8.9 | 7.8 |
| framer | 7.6 | 7.7 |
| shifter | 4.0 | 6.3 |

**Pipeline: ACCEPT share on rogue items when a CHECK was allowed**

| rogue | D0 | D1 | D2 | D1D2 | D3 | D4 | D5 | D6 |
|---|---|---|---|---|---|---|---|---|
| selfish | 0.07 | 0.03 | 0.06 | 0.09 | 0.07 | 0.05 | 0.01 | 0.06 |
| liar | 0.12 | 0.11 | 0.06 | 0.14 | 0.16 | 0.06 | 0.05 | 0.10 |
| framer | 0.11 | 0.08 | 0.10 | 0.08 | 0.09 | 0.12 | 0.18 | 0.09 |
| shifter | 0.06 | 0.10 | 0.07 | 0.12 | 0.09 | 0.08 | 0.03 | 0.06 |

**Pipeline: faulty items accepted by honest members per cell**

| rogue | D0 | D1 | D2 | D1D2 | D3 | D4 | D5 | D6 |
|---|---|---|---|---|---|---|---|---|
| none | 4.0 | 3.8 | 3.7 | 3.8 | 3.5 | 4.0 | 3.9 | 3.8 |
| selfish | 8.2 | 8.6 | 6.6 | 5.9 | 1.9 | 8.3 | 8.2 | 8.2 |
| liar | 9.5 | 9.0 | 8.4 | 7.7 | 2.9 | 9.8 | 9.6 | 9.4 |
| framer | 8.2 | 7.8 | 7.0 | 6.4 | 1.6 | 8.6 | 8.8 | 8.4 |
| shifter | 9.2 | 9.7 | 9.3 | 9.6 | 6.0 | 9.6 | 9.1 | 9.1 |

**Quota: share of cells where the pool ran out**

| rogue | D0 | D1 | D2 | D1D2 | D3 | D4 | D5 | D6 |
|---|---|---|---|---|---|---|---|---|
| none | 0.12 | 0.17 | 0.08 | 0.04 | 0.00 | 0.12 | 0.12 | 0.21 |
| selfish | 0.54 | 0.62 | 0.29 | 0.29 | 0.00 | 0.50 | 0.54 | 0.62 |
| liar | 0.46 | 0.58 | 0.46 | 0.42 | 0.00 | 0.46 | 0.54 | 0.50 |
| framer | 0.46 | 0.62 | 0.25 | 0.08 | 0.00 | 0.58 | 0.46 | 0.58 |
| shifter | 0.50 | 0.58 | 0.50 | 0.54 | 0.00 | 0.62 | 0.46 | 0.67 |

**Quota: units the rogue took per cell**

| rogue | D0 | D1 | D2 | D1D2 | D3 | D4 | D5 | D6 |
|---|---|---|---|---|---|---|---|---|
| selfish | 91.8 | 86.2 | 51.6 | 48.5 | 48.0 | 89.2 | 92.4 | 87.6 |
| liar | 90.2 | 87.1 | 92.1 | 58.6 | 48.0 | 89.9 | 89.9 | 91.4 |
| framer | 88.8 | 85.7 | 69.1 | 58.1 | 48.0 | 88.8 | 93.0 | 88.6 |
| shifter | 90.5 | 89.1 | 90.9 | 91.5 | 48.0 | 86.2 | 90.9 | 88.1 |

**Harm by task (bad rogues)**

| task | D0 | D1 | D2 | D1D2 | D3 | D4 | D5 | D6 |
|---|---|---|---|---|---|---|---|---|
| quota | 0.072 | 0.128 | 0.025 | 0.001 | 0.005 | 0.082 | 0.056 | 0.089 |
| pipeline | 0.208 | 0.218 | 0.135 | 0.188 | 0.059 | 0.223 | 0.220 | 0.217 |

**Output without a rogue (fleet_value, none cells)**

| task | D0 | D1 | D2 | D1D2 | D3 | D4 | D5 | D6 |
|---|---|---|---|---|---|---|---|---|
| quota | 155.7 | 165.5 | 149.7 | 146.6 | 164.4 | 159.5 | 155.6 | 159.7 |
| pipeline | 68.2 | 69.4 | 62.5 | 65.8 | 69.5 | 68.2 | 68.5 | 69.1 |

**D0 harm per model (H-F1)**: ollama_llama2_7b 0.153, ollama_llama3_8b 0.121, ollama_llama31_8b 0.147, ollama_llama32_3b 0.199, ollama_qwen25_7b 0.093, ministral_8b 0.129

**Shifter under exclusion (D2 − D0 harm)** and **H-F7 leave-one-family-out (D3 − D0)**

| comparison | models | estimate | 95% CI |
|---|---|---|---|
| D2 − D0, shifter | 6 | -0.053 | [-0.132, 0.012] |
| D2 − D0, liar | 6 | -0.064 | [-0.142, -0.001] |
| H-F7 without Alibaba | 5 | -0.117 | [-0.157, -0.078] |
| H-F7 without Meta | 2 | -0.063 | [-0.117, -0.008] |
| H-F7 without Mistral | 5 | -0.117 | [-0.157, -0.071] |
