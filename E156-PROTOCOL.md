# E156 Protocol — `MetaFolio`

This repository is the source code and dashboard backing an E156 micro-paper on the [E156 Student Board](https://mahmood726-cyber.github.io/e156/students.html).

---

## `[93]` MetaFolio: Efficiency Frontier Subset Enumeration for Meta-Analysis Heterogeneity Decomposition

**Type:** methods  |  ESTIMAND: I-squared reduction from dominated study exclusion  
**Data:** 10 Cochrane systematic reviews (exhaustive subset enumeration)

### 156-word body

Can subset enumeration identify which studies in a meta-analysis are most responsible for heterogeneity and instability in the pooled estimate? MetaFolio applies exhaustive or sampled subset enumeration to ten Cochrane reviews, computing the efficiency frontier of study subsets ranked by precision and consistency, identifying dominated studies whose removal reduces heterogeneity and narrows confidence intervals. The tool uses DerSimonian-Laird pooling on each candidate subset with coefficient-of-variation stability scoring and influence decomposition quantifying heterogeneity contributions. Across ten reviews, excluding a median of two dominated studies reduced I-squared by 31 percentage points (IQR 18 to 44) without shifting the pooled estimate beyond 0.05 standardized units. Leave-one-out influence decomposition corroborated frontier-based identification, with dominated studies consistently showing the largest heterogeneity contributions. This approach provides a principled alternative to arbitrary outlier removal by grounding exclusion decisions in transparent efficiency trade-offs. However, the limitation of exponential computational scaling means reviews with more than fifteen studies require random sampling rather than exhaustive evaluation.

### Submission metadata

```
Corresponding author: Mahmood Ahmad <mahmood.ahmad2@nhs.net>
ORCID: 0000-0001-9107-3704
Affiliation: Tahir Heart Institute, Rabwah, Pakistan

Links:
  Code:      https://github.com/mahmood726-cyber/MetaFolio
  Protocol:  https://github.com/mahmood726-cyber/MetaFolio/blob/main/E156-PROTOCOL.md
  Dashboard: https://mahmood726-cyber.github.io/metafolio/

References (topic pack: heterogeneity / prediction interval):
  1. Higgins JPT, Thompson SG. 2002. Quantifying heterogeneity in a meta-analysis. Stat Med. 21(11):1539-1558. doi:10.1002/sim.1186
  2. IntHout J, Ioannidis JP, Rovers MM, Goeman JJ. 2016. Plea for routinely presenting prediction intervals in meta-analysis. BMJ Open. 6(7):e010247. doi:10.1136/bmjopen-2015-010247

Data availability: No patient-level data used. Analysis derived exclusively
  from publicly available aggregate records. All source identifiers are in
  the protocol document linked above.

Ethics: Not required. Study uses only publicly available aggregate data; no
  human participants; no patient-identifiable information; no individual-
  participant data. No institutional review board approval sought or required
  under standard research-ethics guidelines for secondary methodological
  research on published literature.

Funding: None.

Competing interests: MA serves on the editorial board of Synthēsis (the
  target journal); MA had no role in editorial decisions on this
  manuscript, which was handled by an independent editor of the journal.

Author contributions (CRediT):
  [STUDENT REWRITER, first author] — Writing – original draft, Writing –
    review & editing, Validation.
  [SUPERVISING FACULTY, last/senior author] — Supervision, Validation,
    Writing – review & editing.
  Mahmood Ahmad (middle author, NOT first or last) — Conceptualization,
    Methodology, Software, Data curation, Formal analysis, Resources.

AI disclosure: Computational tooling (including AI-assisted coding via
  Claude Code [Anthropic]) was used to develop analysis scripts and assist
  with data extraction. The final manuscript was human-written, reviewed,
  and approved by the author; the submitted text is not AI-generated. All
  quantitative claims were verified against source data; cross-validation
  was performed where applicable. The author retains full responsibility for
  the final content.

Preprint: Not preprinted.

Reporting checklist: PRISMA 2020 (methods-paper variant — reports on review corpus).

Target journal: ◆ Synthēsis (https://www.synthesis-medicine.org/index.php/journal)
  Section: Methods Note — submit the 156-word E156 body verbatim as the main text.
  The journal caps main text at ≤400 words; E156's 156-word, 7-sentence
  contract sits well inside that ceiling. Do NOT pad to 400 — the
  micro-paper length is the point of the format.

Manuscript license: CC-BY-4.0.
Code license: MIT.

SUBMITTED: [ ]
```


---

_Auto-generated from the workbook by `C:/E156/scripts/create_missing_protocols.py`. If something is wrong, edit `rewrite-workbook.txt` and re-run the script — it will overwrite this file via the GitHub API._