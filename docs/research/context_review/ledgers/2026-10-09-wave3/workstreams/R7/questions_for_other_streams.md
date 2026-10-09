# Questions for other streams

- Is model/ensemble matching chosen on held-out calibration items or on the evaluation bank? How uncertain is the accuracy match?
- Are arithmetic problems independent draws or variants from common templates? Which resampling unit does the design support?
- Does majority vote mean plurality; what are numerical normalization, invalid-answer and tie rules?
- Are members reused across ensembles and are homogeneous draws cached/reused? How will overlap enter uncertainty estimates?
- Can the resource stream supply actual input/output/reasoning tokens, call counts, retries, latency and price assumptions?
- Does the diversity stream measure complementary correctness and same-wrong-answer collisions conditional on difficulty, or only vendor/persona labels?
- Can topology comparisons keep initial samples and deterministic aggregator identical, with extra communication budget made explicit?
- Is the target claim restricted to independent ensemble accuracy on this bank, or intended to generalize to agent societies and communication? The latter needs separate evidence.
