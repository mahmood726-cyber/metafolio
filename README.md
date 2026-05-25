# MetaFolio

Can subset enumeration identify which studies in a meta-analysis are most responsible for heterogeneity and instability in the pooled estimate? MetaFolio applies exhaustive or sampled subset enumeration to ten Cochrane reviews, computing the efficiency frontier of study subsets ranked by precision and consistency, identifying dominated studies whose removal reduces heterogeneity and narrows confidence intervals. The tool uses DerSimonian-Laird pooling on each candidate subset with coefficient-of-variation stability scoring and influence decomposition quantifying heterogeneity contributions. Across ten reviews, excluding a median of two dominated studies reduced I-squared by 31 percentage points (IQR 18 to 44) without shifting the pooled estimate beyond 0.05 standardized units. Leave-one-out influence decomposition corroborated frontier-based identification, with dominated studies consistently showing the largest heterogeneity contributions. This approach provides a principled alternative to arbitrary outlier removal by grounding exclusion decisions in transparent efficiency trade-offs. However, the limitation of exponential computational scaling means reviews with more than fifteen studies require random sampling rather than exhaustive evaluation.

**Live dashboard:** <https://mahmood726-cyber.github.io/metafolio/>

## Run

Open `template.html` (or `index.html`) in any modern browser. No build step.

For local development:

```bash
python -m http.server 8000
# then open http://localhost:8000/
```

## Test

```bash
python -m pytest -q
```

The suite under `tests/` includes 2 test file(s).

## Repo layout

| Path | Purpose |
|---|---|
| `template.html` | the dashboard (main artifact) |
| `index.html` | landing page |
| `tests/` | pytest tests |
| `e156-submission/` | E156 micro-paper bundle |
| `E156-PROTOCOL.md` | project metadata (E156 entry #93) |

## License

See `LICENSE` (MIT).
