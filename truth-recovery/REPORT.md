# MetaFolio — Truth-Recovery Validation

**Repo:** mahmood726-cyber/metafolio
**Engine under test:** build_portfolio.py (dl_meta, enumerate_subsets_exhaustive, pareto_frontier) — imported VERBATIM, not reimplemented.
**Date:** 2026-06-15

## What MetaFolio does
Enumerates all (or sampled) study subsets, computes a DerSimonian-Laird random-effects pool for each, and surfaces the Pareto-efficient frontier maximizing precision while minimizing between-study heterogeneity (tau2). Also reports leave-one-out influence roles.

## The danger: selection-on-heterogeneity
The frontier rewards low tau2 / high precision. Reporting the "most-efficient subset" is post-selection inference: the subset is chosen because it looks homogeneous, so its SE understates true uncertainty about mu. Measured against known truth using MetaFolio's own functions.

## Method
- DGP A (homogeneous): true mu=0.30, tau2_true=0, k=8. Reference = full-set DL pool. 2000 reps.
- DGP B (two-cluster): core mu=0.30 x6 + outliers mu=1.30 x2. 500 reps.
- Selection strategies: frontier subset with lowest tau2, and highest precision (size >= 3).
- Coverage = fraction of 95% Wald CIs containing true mu.

## Results

### DGP A — homogeneous, tau2_true=0 (2000 reps)
| quantity | full set (ref) | lowest-tau2 subset | highest-prec subset |
|---|---|---|---|
| 95% CI coverage of true mu | 0.961 | 0.929 | 0.930 |
| mean bias | +0.0016 | +0.0003 | +0.0011 |
| mean tau2 reported | 0.0062 | 0.0000 | - |

Under-coverage stable at ~0.929 across min-subset-size 2/3/4. Selected subset reports tau2=0.0000 vs full-set residual 0.0062. Bias essentially nil in symmetric homogeneous design — harm is anti-conservative coverage (~2.7 points below nominal), not point bias.

### DGP B — genuine 2-cluster (500 reps)
| quantity | value |
|---|---|
| mean Jaccard(lowest-tau2 subset, true core) | 0.900 |
| fraction subset is clean core (no outliers) | 0.978 |
| mean bias full pool vs core | +0.253 |
| mean bias lowest-tau2 subset vs core | +0.020 |

When a real homogeneous cluster exists, the frontier recovers it well and is far less contaminated by outliers than the naive full pool.

## Verdict: HONEST-NEGATIVE (mild, well-bounded) + IMPROVEMENT
- Engine math correct (DL pool, Q, tau2, Pareto sweep all verified sane).
- Confirmed selection hazard: reporting the most-efficient subset under-covers true mu (0.929 vs 0.95) and reports tau2=0 by construction even for noisy data. Real, systematic, anti-conservative; not catastrophic (~2.7 pts).
- No point-estimate bias in symmetric homogeneous case; damage is to the interval.
- Frontier is genuinely useful for discovering a real homogeneous subgroup (DGP B).

## Recommendation
Treat the efficient-frontier subset as hypothesis-generating, not a pooled estimate to report. UI should: (1) label any selected-subset CI as post-selection/anti-conservative, not the headline; (2) always show the full-set pool as primary; (3) optionally use split-sample selection before quoting a subset CI.
