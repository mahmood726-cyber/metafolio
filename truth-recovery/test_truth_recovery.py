"""
test_truth_recovery.py — assertions for MetaFolio truth-recovery findings.

Run:  python -m pytest truth-recovery/test_truth_recovery.py -q
  or: python truth-recovery/test_truth_recovery.py
"""
import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_portfolio import dl_meta, enumerate_subsets_exhaustive, pareto_frontier
from harness import run_homogeneous_sim, run_two_cluster_recovery, frontier_picks
from dgp_meta import homogeneous

# Cached sims (Monte-Carlo, deterministic seeds)
_HOM = run_homogeneous_sim(n_sim=2000, k=8, mu=0.30, min_size=3)
_TWO = run_two_cluster_recovery(n_sim=500)


def test_engine_dl_meta_sane():
    """Sanity: repo's dl_meta on a homogeneous draw returns finite est near mu."""
    d = homogeneous(mu=0.30, k=8, seed=0)
    r = dl_meta(d["yi"], d["sei"])
    assert math.isfinite(r["est"]) and math.isfinite(r["se"]) and r["se"] > 0
    assert abs(r["est"] - 0.30) < 0.30  # within a few SE


def test_frontier_zeroes_apparent_heterogeneity():
    """The selected lowest-tau2 subset mechanically reports tau2 ~ 0,
    far below the full-set residual tau2. This is the selection artifact."""
    assert _HOM["mean_tau2_lowest_tau2_subset"] < 1e-6
    assert _HOM["mean_tau2_full"] > _HOM["mean_tau2_lowest_tau2_subset"]


def test_full_set_coverage_is_nominal():
    """Reference (full set, no selection) covers true mu at ~95%."""
    assert 0.93 <= _HOM["coverage_full"] <= 0.97


def test_selection_undercovers_true_mu():
    """KEY FINDING: picking the frontier's lowest-tau2 / highest-precision
    subset under-covers the true mu relative to the full set.
    Selection-on-heterogeneity is anti-conservative."""
    assert _HOM["coverage_lowest_tau2_subset"] < _HOM["coverage_full"] - 0.015
    assert _HOM["coverage_highest_prec_subset"] < _HOM["coverage_full"] - 0.015
    # And both are below the nominal 0.95 floor in absolute terms
    assert _HOM["coverage_lowest_tau2_subset"] < 0.94
    assert _HOM["coverage_highest_prec_subset"] < 0.94


def test_frontier_recovers_real_core_when_one_exists():
    """When a genuine homogeneous core exists, the lowest-tau2 frontier subset
    recovers it cleanly (high Jaccard, usually a clean-core subset) and is far
    less biased toward the outlier cluster than the full pooled estimate."""
    assert _TWO["mean_jaccard_with_core"] > 0.80
    assert _TWO["frac_subset_is_clean_core"] > 0.85
    assert abs(_TWO["mean_bias_lowtau_vs_core"]) < abs(_TWO["mean_bias_full_vs_core"])


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for fn in fns:
        fn()
        print(f"PASS  {fn.__name__}")
        passed += 1
    print(f"\n{passed}/{len(fns)} assertions passed.")
