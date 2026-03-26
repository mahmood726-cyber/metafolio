# MetaFolio Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-file HTML dashboard that applies Markowitz portfolio theory to meta-analysis, showing efficient frontiers, dominated studies, and interactive what-if analysis for study selection.

**Architecture:** Two-phase: (1) Python script enumerates study subsets for 10 reviews, computes DL for each, identifies Pareto frontier, calculates per-study PHR. (2) Single-file HTML dashboard with efficient frontier scatter plot, PHR bar chart, review table, and interactive what-if panel.

**Tech Stack:** Python 3.x (json, math, itertools), vanilla HTML/CSS/JS, SVG for charts.

**Spec:** `C:\MetaFolio\docs\superpowers\specs\2026-03-26-metafolio-design.md`

---

## File Structure

| File | Responsibility |
|------|---------------|
| `C:\MetaFolio\build_portfolio.py` | Enumerate subsets, compute DL, identify frontier, calculate PHR |
| `C:\MetaFolio\data\portfolios.json` | Build artifact |
| `C:\MetaFolio\metafolio.html` | Single-file HTML dashboard (~2,000 lines) |

---

### Task 1: Build `build_portfolio.py`

**Files:**
- Create: `C:\MetaFolio\build_portfolio.py`
- Output: `C:\MetaFolio\data\portfolios.json`

**Context:** For each of the 10 reviews with per-study data, enumerate all non-empty subsets (2^k - 1), compute DL meta-analysis for each, identify the Pareto-efficient frontier, and compute per-study influence metrics (PHR, dominated flag). For k > 15, use greedy + random sampling instead of exhaustive enumeration.

- [ ] **Step 1: Write build_portfolio.py**

Key functions:
- `dl_meta(yi, sei)` — DerSimonian-Laird returning {est, se, tau2, I2, precision}
- `enumerate_subsets(yi, sei)` — for k<=15, all 2^k-1 subsets; for k>15, greedy + 5000 random
- `find_frontier(subsets)` — Pareto-optimal: sort by tau2, sweep for max precision
- `compute_study_metrics(yi, sei, full_meta)` — leave-one-out PHR and dominated flag
- `classify_phr(phr)` — Core/Balanced/Marginal/Dominated

Uses `itertools.combinations` for exhaustive enumeration. Each subset stores: members (list of indices), k_sub, est, se, tau2, I2, precision (1/se^2), on_frontier (bool).

- [ ] **Step 2: Run build script**

```bash
cd /c/MetaFolio && python build_portfolio.py
```

Expected: 10 reviews processed, frontier sizes printed, dominated study counts, JSON output.

- [ ] **Step 3: Verify**

Check that for each review: frontier subsets are truly Pareto-optimal, full-set appears near frontier, dominated studies correctly identified.

- [ ] **Step 4: Commit**

```bash
cd /c/MetaFolio && git add build_portfolio.py data/portfolios.json && git commit -m "feat: portfolio enumeration pipeline — frontiers + PHR for 10 reviews"
```

---

### Task 2: Complete dashboard (scaffold + all features)

**Files:**
- Create: `C:\MetaFolio\metafolio.html`

**Context:** Build the complete dashboard in one pass. Embed portfolio JSON. Implement all sections: summary, table, frontier plot, PHR bars, what-if panel, custom mode, exports.

### CSS
- Light/dark theming, `mf_` localStorage prefix
- Accent color: teal (#0d9488) to distinguish from other tools
- `.stat-grid`, `.card`, `.sortable-table`, `.detail-panel`
- `.frontier-plot` and `.phr-chart` containers
- `.study-core` (green), `.study-balanced` (teal), `.study-marginal` (amber), `.study-dominated` (red)
- What-if panel: `.whatif-panel` with checkbox grid and live stats
- Print styles, responsive

### HTML structure
- Header: "MetaFolio — Evidence Portfolio Optimization", dark mode toggle
- Mode toggle: Corpus / Custom
- Corpus: Summary cards, Review table, Accordion detail (frontier plot + PHR chart)
- Custom: Study input form, Run Analysis, Results (frontier + PHR + what-if panel)
- Footer: version, export buttons

### JS — Statistics engine (for Custom mode)
- `dlMeta(yi, sei)` — DL meta-analysis
- `normalCDF(x)` — for p-values
- `enumerateSubsets(yi, sei, maxK)` — exhaustive for k<=12, greedy+random for k>12 (browser-friendly limit)
- `findFrontier(subsets)` — Pareto sweep
- `computeStudyPHR(yi, sei)` — leave-one-out metrics
- `classifyPHR(phr)` — Core/Balanced/Marginal/Dominated

### JS — Rendering

**`renderSummary()`**: 4 stat boxes from pre-computed data

**`renderReviewTable()`**: Sortable table of 10 reviews. Click to expand.

**`renderFrontierPlot(review)`** — THE CORE VISUALIZATION (SVG ~450x400):
- X-axis: tau² (heterogeneity risk)
- Y-axis: precision (1/SE²)
- Each dot = a subset. Size proportional to k_sub.
- Frontier points: connected with teal line, larger dots, labeled with k_sub
- Full-set point: teal diamond, labeled "Full (k=N)"
- Single-study points: small squares along bottom
- Non-frontier points: small grey dots (dimmed)
- Hover: tooltip showing which studies are included

**`renderPHRChart(review)`** — (SVG bar chart ~300x400):
- Horizontal bars, one per study (indexed or named)
- Length = PHR, color by classification
- Sorted by PHR descending
- Zero-line reference

**`renderWhatIf(yi, sei)`** — Custom mode interactive panel:
- Checkbox per study (all checked initially)
- Live display: current k, pooled est, SE, tau², I², on frontier yes/no
- Highlight current selection on the frontier plot
- Toggle a study → instant recalculation

**Custom mode**: Load Example (8-study set with 2 clearly dominated studies), Run Analysis, frontier + PHR + what-if.

Example:
```javascript
var EXAMPLE = [
  {name:'Alpha 2015', yi:0.30, sei:0.15},
  {name:'Beta 2016', yi:0.25, sei:0.12},
  {name:'Gamma 2016', yi:0.80, sei:0.40},
  {name:'Delta 2017', yi:0.28, sei:0.10},
  {name:'Epsilon 2018', yi:0.35, sei:0.18},
  {name:'Zeta 2018', yi:0.90, sei:0.50},
  {name:'Eta 2019', yi:0.32, sei:0.11},
  {name:'Theta 2020', yi:0.27, sei:0.09}
];
```
(Gamma and Zeta have high SE and extreme effects — likely dominated)

### Export
- CSV: review table + per-study PHR metrics, with csvSafe()
- SVG/PNG: frontier plot, with Blob URL revocation

### Commits
1. `feat: MetaFolio dashboard — frontier plots, PHR charts, what-if panel, custom mode`

### Verification
- Div balance
- No `</script>` in script block
- Summary cards populated
- Click review → frontier scatter + PHR bars render
- Frontier points form a convex-ish upper-left boundary
- Dominated studies highlighted red in PHR chart
- Custom: Load Example → Run → frontier visible, Gamma/Zeta likely dominated
- What-if: uncheck a study → stats + frontier highlight update instantly
- Dark mode, exports work

---

### Task 3: Integration test + index update

- [ ] **Step 1: Full browser test** (all features as per Task 2 verification)
- [ ] **Step 2: Update project index**
- [ ] **Step 3: Final commit**

```bash
cd /c/MetaFolio && git add -A && git commit -m "chore: integration verified, v1.0"
```
