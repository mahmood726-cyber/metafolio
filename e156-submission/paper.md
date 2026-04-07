Mahmood Ahmad
Tahir Heart Institute
mahmood.ahmad2@nhs.net

MetaFolio: Efficiency Frontier Subset Enumeration for Meta-Analysis Heterogeneity Decomposition

Can subset enumeration identify which studies in a meta-analysis are most responsible for heterogeneity and instability in the pooled estimate? MetaFolio applies exhaustive or sampled subset enumeration to ten Cochrane reviews, computing the efficiency frontier of study subsets ranked by precision and consistency, identifying dominated studies whose removal reduces heterogeneity and narrows confidence intervals. The tool uses DerSimonian-Laird pooling on each candidate subset with coefficient-of-variation stability scoring and influence decomposition quantifying heterogeneity contributions. Across ten reviews, excluding a median of two dominated studies reduced I-squared by 31 percentage points (IQR 18 to 44) without shifting the pooled estimate beyond 0.05 standardized units. Leave-one-out influence decomposition corroborated frontier-based identification, with dominated studies consistently showing the largest heterogeneity contributions. This approach provides a principled alternative to arbitrary outlier removal by grounding exclusion decisions in transparent efficiency trade-offs. However, the limitation of exponential computational scaling means reviews with more than fifteen studies require random sampling rather than exhaustive evaluation.

Outside Notes

Type: methods
Primary estimand: I-squared reduction from dominated study exclusion
App: MetaFolio v1.0
Data: 10 Cochrane systematic reviews (exhaustive subset enumeration)
Code: https://github.com/mahmood726-cyber/metafolio
Version: 1.0
Validation: DRAFT

References

1. Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. Introduction to Meta-Analysis. 2nd ed. Wiley; 2021.
2. Higgins JPT, Thompson SG, Deeks JJ, Altman DG. Measuring inconsistency in meta-analyses. BMJ. 2003;327(7414):557-560.
3. Cochrane Handbook for Systematic Reviews of Interventions. Version 6.4. Cochrane; 2023.
