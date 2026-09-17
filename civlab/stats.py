"""Reproducible statistics for agent-civ-lab (added 2026-09-17, Phase 0 rigor pass).

Everything a reviewer needs to re-derive our confidence intervals lives here, keyed to a
fixed method so results are traceable:
  * cluster_bootstrap_ci  — the correct CI when repeated trials share a cluster (e.g. many
    attempts on the SAME word problem, or many rounds within ONE game). Resamples CLUSTERS
    with replacement, keeping all rows within a drawn cluster, then recomputes the statistic.
    A naive per-row bootstrap treats correlated trials as independent and understates width.
  * holm_bonferroni — family-wise multiple-comparison correction for the keyword sweeps
    (8-9 phrase arms tested against one control).
"""
import random, statistics as st

def cluster_bootstrap_ci(clusters, stat=st.mean, iters=5000, alpha=0.05, seed=0):
    """clusters: list of lists; each inner list holds the numeric outcomes of ONE cluster
    (one problem, one game, one agent...). Returns (point, lo, hi) for `stat` over the pooled
    outcomes, with the CI from resampling whole clusters. Point estimate is stat over all rows."""
    rng = random.Random(seed)
    pooled = [x for c in clusters for x in c]
    if not pooled:
        return (float("nan"), float("nan"), float("nan"))
    point = stat(pooled)
    n = len(clusters)
    if n < 2:
        return (point, point, point)
    draws = []
    for _ in range(iters):
        pick = [clusters[rng.randrange(n)] for _ in range(n)]
        rows = [x for c in pick for x in c]
        if rows:
            draws.append(stat(rows))
    draws.sort()
    lo = draws[int((alpha/2)*len(draws))]
    hi = draws[int((1-alpha/2)*len(draws))-1]
    return (point, lo, hi)

def holm_bonferroni(pvalues, alpha=0.05):
    """pvalues: dict name->p. Returns dict name->(p, adjusted_threshold, reject) by Holm's step-down."""
    order = sorted(pvalues.items(), key=lambda kv: kv[1])
    m = len(order); out = {}; still = True
    for i, (name, p) in enumerate(order):
        thresh = alpha / (m - i)
        rej = still and (p <= thresh)
        if not rej: still = False
        out[name] = (p, round(thresh, 5), rej)
    return out

def perm_test_diff(a_clusters, b_clusters, iters=5000, seed=0):
    """Two-sided cluster-permutation test for a difference in means between two arms whose
    unit of independence is the cluster. Returns (diff, p)."""
    rng = random.Random(seed)
    a = [x for c in a_clusters for x in c]; b = [x for c in b_clusters for x in c]
    if not a or not b: return (float("nan"), float("nan"))
    obs = st.mean(a) - st.mean(b)
    pool = list(a_clusters) + list(b_clusters); na = len(a_clusters); hits = 0
    for _ in range(iters):
        rng.shuffle(pool)
        ga = [x for c in pool[:na] for x in c]; gb = [x for c in pool[na:] for x in c]
        if ga and gb and abs(st.mean(ga) - st.mean(gb)) >= abs(obs):
            hits += 1
    return (obs, (hits + 1) / (iters + 1))

if __name__ == "__main__":
    # tiny self-test
    cl = [[1,1,0],[1,0,0],[1,1,1],[0,0,0]]
    print("cluster CI:", [round(x,3) for x in cluster_bootstrap_ci(cl)])
    print("holm:", holm_bonferroni({"a":0.001,"b":0.04,"c":0.20}))
