# Phase C — commons in the dark (PREREG_C)

Model set: confirmatory (prereg/DEVIATIONS.md #1). Valid models analysed: haiku45, ministral_8b, nemotron_super, ollama_llama2_7b, ollama_llama31_8b, ollama_llama32_3b, ollama_llama3_8b, ollama_qwen25_7b

| model | cells | invalid rate | valid | reason |
|---|---:|---:|---|---|
| haiku45 | 64 / 64 | 0.0% | True | ok |
| ministral_8b | 64 / 64 | 0.0% | True | ok |
| nemotron_super | 64 / 64 | 0.2% | True | ok |
| ollama_llama2_7b | 64 / 64 | 0.4% | True | ok |
| ollama_llama31_8b | 64 / 64 | 0.0% | True | ok |
| ollama_llama32_3b | 64 / 64 | 0.0% | True | ok |
| ollama_llama3_8b | 64 / 64 | 0.0% | True | ok |
| ollama_qwen25_7b | 64 / 64 | 0.0% | True | ok |

## Primary (Holm across seven)

| test | hypothesis | n | estimate | 95% CI | p | p (Holm) | sign consistency | survives |
|---|---|---:|---:|---|---:|---:|---:|---|
| H-C1 | Black box: round-1 take differs from the sustainable share (r1_overharvest vs 1; two-sided) | 8 | +0.177 | [-0.848, +2.614] | 0.9844 | 1.0000 | – | False |
| H-C2 | Rules without knowing others (C2) raises the round-1 take vs black box (C0) | 8 | +2.917 | [+0.734, +4.455] | 0.0180 | 0.0720 | 0.875 | False |
| H-C3 | Learning others exist (C3) lowers the round-1 take vs C2 | 8 | -1.330 | [-2.151, -0.410] | 0.0056 | 0.0280 | 0.875 | True |
| H-C4 | Transparency (C4) raises the mean stock vs C3 | 8 | +1.428 | [-2.150, +7.775] | 0.6972 | 1.0000 | 0.5 | False |
| H-C5 | Talk (C5) raises the mean stock vs C4 | 8 | +6.282 | [+0.004, +15.063] | 0.0500 | 0.1500 | 0.625 | False |
| H-C6 | Knowing overreach at C3–C4 exceeds 10% of decisions | 8 | +0.637 | [+0.504, +0.757] | 0.0002 | 0.0012 | 1.0 | True |
| H-C7 | Known end raises the final-round request more than in C4 (endgame_ratio) | 0 | – | – | – | – | – | not testable |

## Secondary (Holm across seven; exploratory)

| test | hypothesis | n | estimate | 95% CI | p | p (Holm) | sign consistency | survives |
|---|---|---:|---:|---|---:|---:|---:|---|
| X1 | One greedy agent: model agents' mean request vs C4 (− compensate, + retaliate/grab) | 8 | +0.070 | [-1.381, +1.410] | 0.8924 | 1.0000 | – | False |
| X2 | Two greedy agents vs one: mean stock (tipping) | 8 | +3.534 | [+0.328, +10.432] | 0.0180 | 0.1080 | – | False |
| X3 | Needy agent's share of points above 25% | 8 | +0.188 | [+0.101, +0.303] | 0.0002 | 0.0014 | 1.0 | True |
| X4 | Others framed as copies of you vs C4: round-1 take | 8 | +0.051 | [-0.412, +0.453] | 0.7952 | 1.0000 | – | False |
| X5 | Others framed as humans vs C4: round-1 take | 8 | -0.060 | [-0.411, +0.260] | 0.7456 | 1.0000 | – | False |
| X6 | Probe control: C0 without the SAFE_TOTAL question vs C0 (round-1 take) | 8 | -0.371 | [-3.047, +1.971] | 0.9180 | 1.0000 | – | False |
| X7 | Probe control: C4 without the SAFE_TOTAL question vs C4 (round-1 take) | 8 | +0.349 | [-0.106, +0.788] | 0.1244 | 0.6220 | – | False |

## Descriptives by arm (mean of model means)

| arm | n_models | mean_stock | overharvest_rate | crash_rounds | never_crashed | recovered | llm_points_mean | r1_overharvest | safe_rate | safe_unknown_rate | safe_abs_err | knowing_overreach | lex_others | lex_future | lex_scarcity |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C0 | 8 | 92.35 | 0.128 | 0.9 | 0.85 | 0.0 | 46.7 | 1.177 | 0.526 | 0.453 | 45.825 | 0.03 | 0.008 | 0.496 | 0.389 |
| C1 | 8 | 17.317 | 0.982 | 9.65 | 0.0 | 0.0 | 38.581 | 3.329 | 0.759 | 0.214 | 13.708 | 0.039 | 0.016 | 0.59 | 0.448 |
| C2 | 8 | 16.115 | 0.978 | 9.8 | 0.0 | 0.0 | 37.869 | 4.094 | 0.919 | 0.066 | 16.677 | 0.022 | 0.007 | 0.861 | 0.358 |
| C3 | 8 | 19.847 | 0.963 | 9.125 | 0.0 | 0.0 | 40.106 | 2.763 | 0.888 | 0.084 | 16.787 | 0.75 | 0.255 | 0.857 | 0.479 |
| C4 | 8 | 21.275 | 0.93 | 8.925 | 0.025 | 0.0 | 40.775 | 2.625 | 0.88 | 0.094 | 16.178 | 0.723 | 0.294 | 0.817 | 0.488 |
| C5 | 8 | 27.558 | 0.912 | 7.775 | 0.075 | 0.1 | 45.537 | 2.699 | 0.949 | 0.031 | 16.77 | 0.593 | 0.467 | 0.796 | 0.438 |
| C0_noprobe | 8 | 85.188 | 0.218 | 1.75 | 0.65 | 0.0 | 53.844 | 0.805 | 0.0 | 0.0 | – | – | 0.006 | 0.087 | 0.054 |
| C4_noprobe | 8 | 16.157 | 0.992 | 9.7 | 0.0 | 0.0 | 37.938 | 2.974 | 0.0 | 0.0 | – | – | 0.334 | 0.531 | 0.419 |
| greedy1 | 8 | 16.128 | 0.997 | 9.75 | 0.0 | 0.0 | 37.49 | 2.586 | 0.881 | 0.102 | 15.756 | 0.665 | 0.269 | 0.803 | 0.523 |
| greedy2 | 8 | 19.663 | 0.969 | 9.25 | 0.0 | 0.0 | 44.422 | 2.59 | 0.853 | 0.122 | 17.697 | 0.61 | 0.289 | 0.786 | 0.539 |
| need | 8 | 22.028 | 0.925 | 8.781 | 0.0 | 0.094 | 42.008 | 2.785 | 0.86 | 0.121 | 23.031 | 0.687 | 0.522 | 0.701 | 0.455 |
| id_copies | 8 | 22.809 | 0.947 | 8.531 | 0.031 | 0.031 | 39.656 | 2.676 | 0.895 | 0.082 | 17.634 | 0.688 | 0.348 | 0.819 | 0.494 |
| id_humans | 8 | 23.547 | 0.938 | 8.781 | 0.0 | 0.031 | 45.047 | 2.565 | 0.87 | 0.093 | 16.874 | 0.712 | 0.349 | 0.805 | 0.484 |
| known_end | 8 | 19.475 | 0.972 | 9.188 | 0.0 | 0.0 | 41.477 | 2.634 | 0.889 | 0.088 | 15.209 | 0.756 | 0.26 | 0.81 | 0.447 |

## Robustness (primary tests under exclusions)

| variant | H-C1 | H-C2 | H-C3 | H-C4 | H-C5 | H-C6 | H-C7 |
|---|---|---|---|---|---|---|---|
| no_pilot_models | -0.769* | +3.617* | -0.964 | +2.397 | +5.650 | +0.590* | – |
| no_haiku | +0.318 | +2.825 | -1.183 | +2.054 | +4.871 | +0.611* | – |
| no_reasoning_models | +0.344 | +3.031 | -1.359 | -0.231 | +3.446 | +0.679* | – |
| leave_out_alibaba | +0.300 | +2.574 | -1.339 | +1.603 | +7.083 | +0.611* | – |
| leave_out_anthropic | +0.318 | +2.825 | -1.183 | +2.054 | +4.871 | +0.611* | – |
| leave_out_meta | -0.823* | +3.482* | -1.467* | +2.660 | +12.890* | +0.599* | – |
| leave_out_mistral | +0.315 | +2.917 | -1.363 | +1.580 | +5.954 | +0.667* | – |
| leave_out_nvidia | +0.344 | +3.031 | -1.359* | -0.231 | +3.446 | +0.679* | – |
