"""
dgp_meta.py — Known-truth data-generating processes for MetaFolio truth-recovery.

Two DGPs:
  - homogeneous(): true single mu, NO real subgroup. tau2_true = 0.
    Any apparent heterogeneity is sampling noise. The "lowest-tau2 / efficient"
    subset is a post-selection artifact; its pooled estimate should be UNbiased
    in expectation only if selection is ignored. We test whether selecting the
    frontier subset induces bias / under-coverage.
  - two_cluster(): a genuine 2-cluster mixture (a real homogeneous core of size
    n_core at mu_core plus n_outlier studies at mu_out). Tests whether the
    frontier recovers the real homogeneous subset.

Returns yi (observed effects), sei (known standard errors), and metadata.
"""
import random
import math


def homogeneous(mu=0.30, k=8, se_lo=0.10, se_hi=0.30, seed=0):
    """True single mu, tau2_true = 0. Observed yi = mu + N(0, sei^2)."""
    rng = random.Random(seed)
    yi, sei = [], []
    for _ in range(k):
        se = rng.uniform(se_lo, se_hi)
        y = mu + rng.gauss(0.0, se)
        yi.append(y)
        sei.append(se)
    return {"yi": yi, "sei": sei, "mu_true": mu, "tau2_true": 0.0, "k": k}


def two_cluster(mu_core=0.30, mu_out=1.20, n_core=6, n_out=2,
                se_lo=0.10, se_hi=0.25, seed=0):
    """
    Genuine 2-cluster: n_core homogeneous studies at mu_core (tau2=0 within),
    plus n_out outlier studies at mu_out. The 'real homogeneous subset' is the
    core cluster (indices 0..n_core-1). The pooled mu of the WHOLE set is biased
    toward mu_out; the core subset recovers mu_core.
    """
    rng = random.Random(seed)
    yi, sei = [], []
    core_idx = list(range(n_core))
    for _ in range(n_core):
        se = rng.uniform(se_lo, se_hi)
        yi.append(mu_core + rng.gauss(0.0, se))
        sei.append(se)
    for _ in range(n_out):
        se = rng.uniform(se_lo, se_hi)
        yi.append(mu_out + rng.gauss(0.0, se))
        sei.append(se)
    return {"yi": yi, "sei": sei, "mu_core": mu_core, "mu_out": mu_out,
            "core_idx": set(core_idx), "k": n_core + n_out}


def normal_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))
