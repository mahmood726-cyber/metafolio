# MetaFolio Design Spec — Portfolio Theory for Evidence Synthesis

**Date:** 2026-03-26
**Target:** `C:\MetaFolio\metafolio.html` (new single-file HTML app)
**Build step:** `C:\MetaFolio\build_portfolio.py` (new Python script)
**Data source:** `C:\FragilityAtlas\data\output\r_validation_inputs.json` (10 analyses with per-study yi/sei)

## Background

Markowitz portfolio theory (1952) optimizes asset allocation by maximizing expected return for a given risk level. The "efficient frontier" shows the set of optimal portfolios. We apply this to meta-analysis: studies are assets, precision is return, heterogeneity is risk, and the efficient frontier shows which study subsets maximize precision for a given heterogeneity budget.

No one has applied portfolio theory to meta-analysis study selection. This reframes the question from "include everything" to "what's the optimal evidence portfolio?"

## 1. The Analogy

| Finance Concept | Meta-Analysis Mapping |
|-----------------|----------------------|
| Asset | Study |
| Expected return | Precision contribution (1/SE² weight) |
| Risk (variance) | Contribution to heterogeneity (tau²) |
| Portfolio | Subset of studies pooled via DL |
| Efficient frontier | Pareto-optimal subsets: max precision for given tau² |
| Diversification benefit | Heterogeneous populations reduce pooling variance |
| Dominated asset | Study adding heterogeneity without improving precision |
| Sharpe ratio | Precision-to-Heterogeneity Ratio (PHR) |

## 2. Data Pipeline

### `build_portfolio.py`

Load 10 reviews with per-study data from `r_validation_inputs.json`.

For each review with k studies:

**If k <= 15 (2^k <= 32,768):** Enumerate all non-empty subsets. For each subset, compute DL meta-analysis: pooled estimate, SE, tau², I².

**If k > 15:** Use greedy forward-selection:
1. Start with the study having lowest SE
2. At each step, add the study maximizing PHR (precision gain / heterogeneity cost)
3. Also run 5,000 random subsets of sizes 2..k-1 for frontier estimation
4. Combine greedy path + random subsets

For each subset, record: `{members: [indices], k_sub, est, se, tau2, I2, precision: 1/se^2}`.

**Identify efficient frontier:** Pareto-optimal subsets where no other subset dominates in both precision AND tau². A subset S dominates T if `precision(S) >= precision(T)` AND `tau2(S) <= tau2(T)` (with at least one strict inequality).

**Per-study influence metrics (leave-one-out):**
- `delta_se_i = se_full - se_{-i}` (positive = study improves precision)
- `delta_tau2_i = tau2_full - tau2_{-i}` (positive = study increases heterogeneity)
- `PHR_i = delta_se_i / max(|delta_tau2_i|, 1e-8)` (precision gain per unit heterogeneity)
- `dominated = (delta_se_i <= 0 AND delta_tau2_i > 0)` — removing it improves both

### Output: `data/portfolios.json`

```json
{
  "reviews": [
    {
      "review_id": "CD006140",
      "analysis_name": "Acceptability",
      "k": 8,
      "studies": [
        {"idx": 0, "yi": -0.821, "sei": 0.329, "phr": 1.23, "dominated": false,
         "delta_se": 0.015, "delta_tau2": 0.012}
      ],
      "full_meta": {"est": -0.15, "se": 0.025, "tau2": 0.03, "I2": 45.2},
      "subsets": [
        {"members": [0,1,2], "k_sub": 3, "est": -0.20, "se": 0.035, "tau2": 0.01,
         "precision": 816.3, "on_frontier": true}
      ],
      "frontier_indices": [0, 5, 12, 45],
      "n_dominated": 2,
      "enumeration_method": "exhaustive"
    }
  ],
  "corpus_summary": {
    "n_reviews": 10,
    "avg_k": 15.2,
    "avg_pct_dominated": 18.5,
    "avg_frontier_size": 12
  }
}
```

## 3. Statistical Methods

### DerSimonian-Laird (same as MetaShift)

Standard DL pooling for each subset. Returns est, se, tau2, I2.

### Efficient frontier identification

Given all evaluated subsets as points in (tau2, precision) space:
1. Sort by tau2 ascending
2. Sweep: a point is on the frontier if its precision exceeds all points with lower tau2
3. Connect frontier points to form the efficient frontier curve

### Precision-to-Heterogeneity Ratio (PHR)

Per-study metric analogous to the Sharpe ratio:

```
PHR_i = (SE_{-i} - SE_full) / max(tau2_full - tau2_{-i}, epsilon)
```

Where:
- Numerator: how much worse precision gets without study i (positive = study helps)
- Denominator: how much heterogeneity study i contributes (positive = study adds het)
- High PHR = study contributes more precision than heterogeneity (keep it)
- Negative numerator + positive denominator = dominated (remove it)

Classification:
- **Core** (PHR > 1): high precision gain, moderate het cost
- **Balanced** (PHR 0.5-1): decent trade-off
- **Marginal** (PHR 0-0.5): low value-add
- **Dominated** (PHR < 0 or removing improves both): should consider excluding

## 4. Dashboard Layout

Single scrollable page, dark mode toggle. Two modes: Corpus and Custom.

### Header

- Title: "MetaFolio — Evidence Portfolio Optimization"
- Subtitle: "Markowitz efficient frontier applied to meta-analysis study selection"
- Mode toggle: [Corpus | Custom]

### Corpus Mode

**Section 1 — Corpus Summary**: 4 stat boxes:
1. Reviews analyzed (10)
2. Average k (study count)
3. Average % dominated studies
4. Average frontier size (% of subsets on frontier)

**Section 2 — Review Explorer**: Sortable table:
| Review ID | Analysis | k | Dominated | Frontier | Method |
Click to expand.

**Section 3 — Expanded Detail** (accordion): Two panels:

**Left — Efficient Frontier Plot** (SVG, ~400x400px):
- X-axis: tau² (heterogeneity)
- Y-axis: precision (1/SE²)
- Dots: each evaluated subset, sized by k_sub
- Frontier subsets: connected with blue line, larger dots
- Full-set point: marked with diamond
- Single-study points: marked with squares at bottom
- Dominated subsets: dimmed/greyed
- Hover tooltip: shows which studies are in the subset

**Right — Study PHR Chart** (SVG bar chart, ~300x400px):
- Horizontal bars, one per study
- Bar length = PHR value
- Color: green (Core), blue (Balanced), amber (Marginal), red (Dominated)
- Sorted by PHR descending
- Study label on left

**Section 4 — Dominated Studies Summary**: Table across all 10 reviews:
| Review | Study idx | Effect | SE | delta_tau2 | Classification |

### Custom Mode

**Input**: Table with rows [Study Name, Effect, SE]. "Add Study" / "Clear" / "Load Example".

**Analysis**: "Run Portfolio Analysis" button. For k <= 15, exhaustive enumeration. For k > 15, greedy + random sampling.

**Results**:
- Efficient frontier plot (same as corpus)
- Study PHR bars
- **What-If Panel**: Checkbox per study. Toggling a study ON/OFF live-updates:
  - Pooled estimate + CI
  - Current position on the frontier plot (highlighted dot)
  - Summary: "Current selection: k=X, precision=Y, tau²=Z, on frontier: yes/no"

The what-if panel is the prescriptive killer feature — drag the evidence portfolio along the frontier interactively.

### Footer

- "MetaFolio v1.0 — Browser-based, no data leaves your device."
- Export: [CSV] table, [SVG] frontier plot, [PNG] frontier plot
- localStorage prefix: `mf_`

## 5. Visual Design

Same portfolio CSS pattern. Accent color: teal (#0d9488) to distinguish from the blue-themed tools.

## 6. Integration Map

| File | Purpose |
|------|---------|
| `C:\MetaFolio\build_portfolio.py` | Enumerate subsets, compute frontiers, per-study PHR |
| `C:\MetaFolio\data\portfolios.json` | Build artifact |
| `C:\MetaFolio\metafolio.html` | Single-file HTML dashboard (~2,000 lines) |

## 7. Out of Scope

- Covariance between studies (assume independence)
- Multi-outcome optimization
- Transaction cost analogy
- Mean-variance optimization with user constraints
- Short-selling analogy (negative weights)

## 8. Validation

- For k=3 (8 subsets): verify all subsets enumerated, frontier correct by inspection
- For k=8: verify frontier is Pareto-optimal (no dominated frontier point)
- PHR computation: manually verify for one study against leave-one-out DL results
- Full-set point should always appear on or near the frontier (it uses all info)
- Dominated studies: verify that removing them reduces tau² without increasing SE
- Custom mode what-if: toggling a study recalculates and repositions correctly
