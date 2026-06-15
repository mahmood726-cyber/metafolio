"""
harness.py — Truth-recovery harness for MetaFolio.

Wires MetaFolio's OWN engine functions (build_portfolio.dl_meta,
enumerate_subsets_exhaustive, pareto_frontier) against known-truth DGPs.

CENTRAL QUESTION (selection-on-heterogeneity):
  MetaFolio enumerates all study subsets and surfaces the Pareto frontier
  (max precision, min tau2). If an analyst then *reports the most-efficient
  subset* (highest precision on the frontier, or the lowest-tau2 subset),
  that is post-selection inference. We measure, against a known-truth
  HOMOGENEOUS meta-analysis (true single mu, tau2_true = 0):

    1. Selection bias of the "best subset" pooled estimate vs the full-set
       pooled estimate (which is the unbiased reference).
    2. Wald 95% CI coverage of true mu for:
         (a) the FULL set (reference, should be ~95%)
         (b) the LOWEST-TAU2 subset on the frontier
         (c) the HIGHEST-PRECISION subset on the frontier
       Under-coverage of (b)/(c) demonstrates the selection hazard.

  And against a true 2-cluster DGP: does the frontier's lowest-tau2 /
  best subset recover the real homogeneous core cluster?

Run:  python truth-recovery/harness.py
"""
import sys
import math
from pathlib import Path

# Import MetaFolio's own engine
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from build_portfolio import dl_meta, enumerate_subsets_exhaustive, pareto_frontier

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dgp_meta import homogeneous, two_cluster, normal_cdf

Z = 1.959963984540054  # qnorm(0.975)


def all_subset_results(yi, sei):
    """Compute dl_meta for every non-empty subset (repo's own enumerator)."""
    subsets = enumerate_subsets_exhaustive(len(yi))
    results = []
    for sub in subsets:
        ys = [yi[i] for i in sub]
        ss = [sei[i] for i in sub]
        r = dl_meta(ys, ss)
        r = dict(r)
        r["indices"] = sub
        r["size"] = len(sub)
        results.append(r)
    return subsets, results


def frontier_picks(yi, sei, min_size=3):
    """
    Use the repo's pareto_frontier to get efficient subsets, then identify two
    selection strategies an analyst would plausibly use:
      - lowest_tau2: frontier subset with the smallest tau2 (most 'homogeneous')
      - highest_prec: frontier subset with the largest precision
    Restrict to size >= min_size so we don't trivially pick a single study
    (k=1 always has tau2=0); this is the realistic 'pick a clean subset' move.
    """
    subsets, results = all_subset_results(yi, sei)
    fidx = pareto_frontier(results)
    front = [results[i] for i in fidx if results[i]["size"] >= min_size]
    if not front:  # fallback: allow any size
        front = [results[i] for i in fidx]
    lowest_tau2 = min(front, key=lambda r: (r["tau2"], -r["precision"]))
    highest_prec = max(front, key=lambda r: r["precision"])
    return lowest_tau2, highest_prec, results


def covers(est, se, mu):
    if not (math.isfinite(est) and math.isfinite(se) and se > 0):
        return False
    return (est - Z * se) <= mu <= (est + Z * se)


def run_homogeneous_sim(n_sim=2000, k=8, mu=0.30, min_size=3, seed0=1000):
    """Monte-Carlo: measure selection bias + coverage under tau2_true=0."""
    cov_full = cov_lowtau = cov_highprec = 0
    bias_full = bias_lowtau = bias_highprec = 0.0
    tau2_full_sum = tau2_lowtau_sum = 0.0
    for s in range(n_sim):
        d = homogeneous(mu=mu, k=k, seed=seed0 + s)
        yi, sei = d["yi"], d["sei"]

        full = dl_meta(yi, sei)
        lowtau, highprec, _ = frontier_picks(yi, sei, min_size=min_size)

        cov_full += covers(full["est"], full["se"], mu)
        cov_lowtau += covers(lowtau["est"], lowtau["se"], mu)
        cov_highprec += covers(highprec["est"], highprec["se"], mu)

        bias_full += full["est"] - mu
        bias_lowtau += lowtau["est"] - mu
        bias_highprec += highprec["est"] - mu

        tau2_full_sum += full["tau2"]
        tau2_lowtau_sum += lowtau["tau2"]

    return {
        "n_sim": n_sim, "k": k, "mu_true": mu, "min_size": min_size,
        "coverage_full": cov_full / n_sim,
        "coverage_lowest_tau2_subset": cov_lowtau / n_sim,
        "coverage_highest_prec_subset": cov_highprec / n_sim,
        "mean_bias_full": bias_full / n_sim,
        "mean_bias_lowest_tau2_subset": bias_lowtau / n_sim,
        "mean_bias_highest_prec_subset": bias_highprec / n_sim,
        "mean_tau2_full": tau2_full_sum / n_sim,
        "mean_tau2_lowest_tau2_subset": tau2_lowtau_sum / n_sim,
    }


def run_two_cluster_recovery(n_sim=500, mu_core=0.30, mu_out=1.30,
                             n_core=6, n_out=2, min_size=3, seed0=7000):
    """
    Does the frontier's lowest-tau2 subset recover the real homogeneous core?
    We measure:
      - jaccard(lowtau_subset, core_idx) averaged
      - fraction of sims where lowtau subset is a SUBSET of the true core
        (i.e., it correctly excludes all outliers)
      - bias of lowtau subset toward mu_core vs bias of full set
    """
    jac_sum = 0.0
    clean_core = 0  # lowtau subset contains only core studies
    bias_full_to_core = 0.0
    bias_lowtau_to_core = 0.0
    for s in range(n_sim):
        d = two_cluster(mu_core=mu_core, mu_out=mu_out, n_core=n_core,
                        n_out=n_out, seed=seed0 + s)
        yi, sei, core = d["yi"], d["sei"], d["core_idx"]
        full = dl_meta(yi, sei)
        lowtau, _, _ = frontier_picks(yi, sei, min_size=min_size)
        sub = set(lowtau["indices"])
        inter = len(sub & core)
        union = len(sub | core)
        jac_sum += inter / union if union else 0.0
        if sub.issubset(core):
            clean_core += 1
        bias_full_to_core += full["est"] - mu_core
        bias_lowtau_to_core += lowtau["est"] - mu_core
    return {
        "n_sim": n_sim, "mu_core": mu_core, "mu_out": mu_out,
        "mean_jaccard_with_core": jac_sum / n_sim,
        "frac_subset_is_clean_core": clean_core / n_sim,
        "mean_bias_full_vs_core": bias_full_to_core / n_sim,
        "mean_bias_lowtau_vs_core": bias_lowtau_to_core / n_sim,
    }


if __name__ == "__main__":
    print("=" * 70)
    print("MetaFolio truth-recovery: selection-on-heterogeneity")
    print("=" * 70)
    print("\n[1] HOMOGENEOUS DGP (true single mu=0.30, tau2_true=0, k=8)")
    print("    Reference = full set. Selection = pick frontier subset.\n")
    h = run_homogeneous_sim(n_sim=2000, k=8, mu=0.30, min_size=3)
    for kk, vv in h.items():
        print(f"    {kk:34s} = {vv:.4f}" if isinstance(vv, float) else f"    {kk:34s} = {vv}")

    print("\n[2] TWO-CLUSTER DGP (core mu=0.30 x6, outliers mu=1.30 x2)")
    print("    Does lowest-tau2 frontier subset recover the real core?\n")
    t = run_two_cluster_recovery(n_sim=500)
    for kk, vv in t.items():
        print(f"    {kk:34s} = {vv:.4f}" if isinstance(vv, float) else f"    {kk:34s} = {vv}")
    print("\nDone.")
