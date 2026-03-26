"""
build_portfolio.py — MetaFolio Task 1: Portfolio Enumeration Pipeline
Loads per-study meta-analysis data, enumerates subsets, computes DL meta for each,
identifies Pareto-efficient frontiers (precision vs tau2), and computes PHR influence metrics.

Input:  C:/FragilityAtlas/data/output/r_validation_inputs.json
Output: C:/MetaFolio/data/portfolios.json
"""

import json
import math
import random
import itertools
import os
from typing import List, Tuple, Dict, Any, Optional

# ─── DerSimonian-Laird meta-analysis ──────────────────────────────────────────

def dl_meta(yi: List[float], sei: List[float]) -> Dict[str, float]:
    """
    Compute DerSimonian-Laird random-effects meta-analysis.
    Returns dict with: est, se, tau2, I2, precision.
    For k=1: returns single-study result directly.
    """
    k = len(yi)
    assert k >= 1, "Need at least 1 study"
    assert len(sei) == k, "yi and sei must be same length"

    if k == 1:
        se = sei[0]
        prec = 1.0 / (se * se) if math.isfinite(se) and se > 0 else 0.0
        return {
            "est": yi[0],
            "se": se,
            "tau2": 0.0,
            "I2": 0.0,
            "precision": prec,
        }

    # Fixed-effect weights: w_i = 1/sei^2
    wi = []
    for s in sei:
        if math.isfinite(s) and s > 0:
            wi.append(1.0 / (s * s))
        else:
            wi.append(0.0)

    W = sum(wi)
    if W <= 0:
        return {"est": float("nan"), "se": float("nan"), "tau2": float("nan"), "I2": float("nan"), "precision": 0.0}

    # Cochran's Q
    theta_fe = sum(wi[i] * yi[i] for i in range(k)) / W
    Q = sum(wi[i] * (yi[i] - theta_fe) ** 2 for i in range(k))

    # DL tau2 estimator
    W2 = sum(w * w for w in wi)
    c = W - W2 / W
    df = k - 1
    tau2 = max(0.0, (Q - df) / c) if c > 0 else 0.0

    # Random-effect weights: w*_i = 1/(sei^2 + tau2)
    wi_star = []
    for s in sei:
        denom = s * s + tau2
        if math.isfinite(denom) and denom > 0:
            wi_star.append(1.0 / denom)
        else:
            wi_star.append(0.0)

    W_star = sum(wi_star)
    if W_star <= 0:
        return {"est": float("nan"), "se": float("nan"), "tau2": tau2, "I2": float("nan"), "precision": 0.0}

    est = sum(wi_star[i] * yi[i] for i in range(k)) / W_star
    var_est = 1.0 / W_star
    se = math.sqrt(var_est) if var_est >= 0 else float("nan")
    precision = W_star if math.isfinite(W_star) else 0.0

    # I2 = max(0, (Q - df) / Q) * 100  [conventional, not DL tau2-based]
    I2 = max(0.0, (Q - df) / Q * 100.0) if Q > 0 else 0.0

    return {"est": est, "se": se, "tau2": tau2, "I2": I2, "precision": precision}


# ─── Subset enumeration ────────────────────────────────────────────────────────

def enumerate_subsets_exhaustive(k: int) -> List[Tuple[int, ...]]:
    """Return all non-empty subsets of indices 0..k-1 as tuples."""
    indices = list(range(k))
    subsets = []
    for size in range(1, k + 1):
        for combo in itertools.combinations(indices, size):
            subsets.append(combo)
    return subsets


def greedy_forward_path(yi: List[float], sei: List[float]) -> List[Tuple[int, ...]]:
    """
    Greedy forward selection: start with empty set, at each step add the study
    that most increases precision (lowest effective SE). Returns list of subsets
    (each a frozenset-style tuple), one per step from size 1 to k.
    """
    k = len(yi)
    remaining = set(range(k))
    selected = []
    path = []
    while remaining:
        best_idx = None
        best_prec = -1.0
        for idx in remaining:
            candidate = selected + [idx]
            yi_c = [yi[i] for i in candidate]
            sei_c = [sei[i] for i in candidate]
            res = dl_meta(yi_c, sei_c)
            if math.isfinite(res["precision"]) and res["precision"] > best_prec:
                best_prec = res["precision"]
                best_idx = idx
        if best_idx is None:
            break
        selected.append(best_idx)
        remaining.remove(best_idx)
        path.append(tuple(sorted(selected)))
    return path


def enumerate_subsets_sampling(
    yi: List[float], sei: List[float], n_random: int = 5000, seed: int = 42
) -> List[Tuple[int, ...]]:
    """
    For large k (>15): greedy forward path + n_random random subsets.
    Uses xoshiro128**-style seeded RNG (via random.seed) for reproducibility.
    Returns list of unique subset tuples.
    """
    k = len(yi)
    seen = set()
    subsets = []

    # 1) Greedy path (k subsets)
    greedy_path = greedy_forward_path(yi, sei)
    for s in greedy_path:
        if s not in seen:
            seen.add(s)
            subsets.append(s)

    # 2) Random subsets
    rng = random.Random(seed)
    attempts = 0
    max_attempts = n_random * 10
    while len(subsets) - len(greedy_path) < n_random and attempts < max_attempts:
        attempts += 1
        size = rng.randint(1, k)
        combo = tuple(sorted(rng.sample(range(k), size)))
        if combo not in seen:
            seen.add(combo)
            subsets.append(combo)

    return subsets


# ─── Pareto frontier ──────────────────────────────────────────────────────────

def pareto_frontier(results: List[Dict[str, Any]]) -> List[int]:
    """
    Identify Pareto-efficient subsets: maximize precision AND minimize tau2.
    A subset is on the frontier if no other subset has both >= precision AND <= tau2
    (strictly better in at least one).

    Algorithm: sort by tau2 ascending; sweep keeping track of max precision seen.
    A point is on the frontier if its precision exceeds the max precision of all
    points with strictly lower tau2 (i.e., it's not dominated).
    """
    # Filter to finite results only
    valid = [(i, r) for i, r in enumerate(results)
             if math.isfinite(r["precision"]) and math.isfinite(r["tau2"])]

    if not valid:
        return []

    # Sort by tau2 ascending, then precision descending (for ties)
    valid_sorted = sorted(valid, key=lambda x: (x[1]["tau2"], -x[1]["precision"]))

    frontier_indices = []
    max_prec_so_far = -1.0

    for orig_idx, r in valid_sorted:
        prec = r["precision"]
        if prec > max_prec_so_far:
            frontier_indices.append(orig_idx)
            max_prec_so_far = prec

    return frontier_indices


# ─── Per-study influence (leave-one-out) ──────────────────────────────────────

def compute_influence(yi: List[float], sei: List[float]) -> List[Dict[str, Any]]:
    """
    Leave-one-out influence analysis.
    delta_se   = se_loo   - se_full    (positive => removing study worsens SE => study helps precision)
    delta_tau2 = tau2_full - tau2_loo  (positive => study adds heterogeneity; removing it reduces tau2)
    Returns list of dicts with: delta_se, delta_tau2, PHR, dominated, role.
    """
    k = len(yi)
    full = dl_meta(yi, sei)
    se_full = full["se"]
    tau2_full = full["tau2"]

    influences = []
    for i in range(k):
        yi_loo = [yi[j] for j in range(k) if j != i]
        sei_loo = [sei[j] for j in range(k) if j != i]
        if len(yi_loo) == 0:
            influences.append({
                "study_index": i,
                "delta_se": 0.0,
                "delta_tau2": 0.0,
                "PHR": 0.0,
                "dominated": False,
                "role": "Core",
            })
            continue

        loo = dl_meta(yi_loo, sei_loo)

        # delta_se > 0 means study helps precision (removing it worsens se: se_loo > se_full)
        delta_se = (loo["se"] - se_full) if (math.isfinite(se_full) and math.isfinite(loo["se"])) else 0.0
        # delta_tau2 > 0 means study adds heterogeneity (removing it reduces tau2: tau2_full > tau2_loo)
        delta_tau2 = (tau2_full - loo["tau2"]) if (math.isfinite(tau2_full) and math.isfinite(loo["tau2"])) else 0.0

        PHR = delta_se / max(abs(delta_tau2), 1e-8)

        # Dominated: removing the study improves BOTH precision (delta_se <= 0) AND tau2 (delta_tau2 > 0)
        dominated = (delta_se <= 0) and (delta_tau2 > 0)

        # PHR-based role
        if dominated or PHR < 0:
            role = "Dominated"
        elif PHR < 0.5:
            role = "Marginal"
        elif PHR < 1.0:
            role = "Balanced"
        else:
            role = "Core"

        influences.append({
            "study_index": i,
            "delta_se": delta_se,
            "delta_tau2": delta_tau2,
            "PHR": PHR,
            "dominated": dominated,
            "role": role,
        })

    return influences


# ─── Main pipeline ─────────────────────────────────────────────────────────────

def process_review(review: Dict[str, Any], max_sample_non_frontier: int = 500) -> Dict[str, Any]:
    """Process a single review: enumerate subsets, compute DL meta, find frontier."""
    review_id = review["review_id"]
    analysis_name = review["analysis_name"]
    k = review["k"]
    yi = review["yi"]
    sei = review["sei"]

    assert len(yi) == k
    assert len(sei) == k

    # ── Enumerate subsets ──
    if k <= 15:
        subsets = enumerate_subsets_exhaustive(k)
        enumeration_method = "exhaustive"
    else:
        subsets = enumerate_subsets_sampling(yi, sei, n_random=5000, seed=42)
        enumeration_method = "greedy+random"

    n_subsets = len(subsets)

    # ── Compute DL meta for each subset ──
    subset_results = []
    for subset in subsets:
        yi_s = [yi[i] for i in subset]
        sei_s = [sei[i] for i in subset]
        res = dl_meta(yi_s, sei_s)
        subset_results.append({
            "indices": list(subset),
            "size": len(subset),
            **res,
        })

    # ── Pareto frontier ──
    frontier_idx_set = set(pareto_frontier(subset_results))
    for idx in range(len(subset_results)):
        subset_results[idx]["on_frontier"] = idx in frontier_idx_set

    n_frontier = len(frontier_idx_set)

    # ── Influence metrics (full set) ──
    full_meta = dl_meta(yi, sei)
    influences = compute_influence(yi, sei)
    n_dominated = sum(1 for inf in influences if inf["dominated"])

    # ── Stability: coefficient of variation of frontier precisions ──
    frontier_precs = [subset_results[i]["precision"] for i in frontier_idx_set
                      if math.isfinite(subset_results[i]["precision"])]
    if len(frontier_precs) > 1:
        mean_p = sum(frontier_precs) / len(frontier_precs)
        std_p = math.sqrt(sum((p - mean_p) ** 2 for p in frontier_precs) / len(frontier_precs))
        stability_cv = std_p / mean_p if mean_p > 0 else float("nan")
    else:
        stability_cv = 0.0

    # ── Downsample non-frontier subsets to keep output size manageable ──
    frontier_subsets = [r for i, r in enumerate(subset_results) if i in frontier_idx_set]
    non_frontier_all = [r for i, r in enumerate(subset_results) if i not in frontier_idx_set]

    # Sample non-frontier (seed-stable)
    rng = random.Random(99)
    if len(non_frontier_all) > max_sample_non_frontier:
        non_frontier_sample = rng.sample(non_frontier_all, max_sample_non_frontier)
    else:
        non_frontier_sample = non_frontier_all

    all_stored = frontier_subsets + non_frontier_sample

    return {
        "review_id": review_id,
        "analysis_name": analysis_name,
        "k": k,
        "enumeration_method": enumeration_method,
        "n_subsets_evaluated": n_subsets,
        "n_frontier": n_frontier,
        "n_dominated_studies": n_dominated,
        "stability_cv": stability_cv if math.isfinite(stability_cv) else None,
        "full_meta": full_meta,
        "influences": influences,
        "subsets": all_stored,
    }


def main():
    input_path = r"C:\FragilityAtlas\data\output\r_validation_inputs.json"
    output_path = r"C:\MetaFolio\data\portfolios.json"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"Loading {input_path} ...")
    with open(input_path, "r", encoding="utf-8") as f:
        reviews = json.load(f)

    print(f"Loaded {len(reviews)} reviews.\n")

    portfolios = []
    summary_rows = []

    for rev in reviews:
        k = rev["k"]
        review_id = rev["review_id"]
        analysis = rev["analysis_name"]
        print(f"  Processing {review_id} | k={k:3d} | {analysis[:50]}")

        result = process_review(rev)
        portfolios.append(result)

        # Summary row
        full = result["full_meta"]
        dominated_roles = [inf["role"] for inf in result["influences"]]
        role_counts = {r: dominated_roles.count(r) for r in ["Core", "Balanced", "Marginal", "Dominated"]}

        stability_str = f"{result['stability_cv']:.3f}" if result["stability_cv"] is not None else "N/A"

        summary_rows.append({
            "review_id": review_id,
            "k": k,
            "n_subsets": result["n_subsets_evaluated"],
            "n_frontier": result["n_frontier"],
            "n_dominated_studies": result["n_dominated_studies"],
            "stability_cv": stability_str,
            "full_est": f"{full['est']:.4f}" if math.isfinite(full["est"]) else "NaN",
            "full_se": f"{full['se']:.4f}" if math.isfinite(full["se"]) else "NaN",
            "full_tau2": f"{full['tau2']:.4f}" if math.isfinite(full["tau2"]) else "NaN",
            "full_I2": f"{full['I2']:.1f}" if math.isfinite(full["I2"]) else "NaN",
            "role_Core": role_counts["Core"],
            "role_Balanced": role_counts["Balanced"],
            "role_Marginal": role_counts["Marginal"],
            "role_Dominated": role_counts["Dominated"],
        })

    # ── Save output ──
    print(f"\nSaving portfolios to {output_path} ...")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(portfolios, f, indent=2, allow_nan=False)
    print(f"Saved. File size: {os.path.getsize(output_path) / 1024:.1f} KB\n")

    # ── Print summary table ──
    print("=" * 120)
    print(f"{'Review':12s} {'k':>4s} {'Subsets':>10s} {'Frontier':>9s} {'Dom_Studies':>12s} {'Stab_CV':>9s} "
          f"{'Est':>8s} {'SE':>7s} {'tau2':>8s} {'I2':>6s} "
          f"{'Core':>5s} {'Bal':>5s} {'Marg':>5s} {'Dom':>5s}")
    print("-" * 120)
    for row in summary_rows:
        print(
            f"{row['review_id']:12s} {row['k']:4d} {row['n_subsets']:10,d} {row['n_frontier']:9d} "
            f"{row['n_dominated_studies']:12d} {row['stability_cv']:>9s} "
            f"{row['full_est']:>8s} {row['full_se']:>7s} {row['full_tau2']:>8s} {row['full_I2']:>6s} "
            f"{row['role_Core']:5d} {row['role_Balanced']:5d} {row['role_Marginal']:5d} {row['role_Dominated']:5d}"
        )
    print("=" * 120)
    print("\nDone.")


if __name__ == "__main__":
    main()
