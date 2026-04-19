# ✅ Pre-Submission Checklist — NeurIPS 2025

## Paper Formatting
- [ ] Page limit: 9 pages (main) + unlimited references + appendix
- [ ] Use `\usepackage[review]{neurips_2024}` (anonymous + line numbers)
- [ ] **COMMENT OUT author name** (line 101-104 in .tex — currently visible!)
- [ ] Remove any identifying info from code/data
- [ ] All figures are PDF/vector (not rasterized)

## Empirical Claims Verification
- [ ] Table 4 (benchmark results): All 9 benchmarks scored, CIs computed
- [ ] Table 5 (human eval): N=444 (or adjusted), all p-values, Cohen's d, CIs
- [ ] Table 3 (learned predictor): Test + X-Bench + Zero-shot metrics
- [ ] Table 2 (perturbations): σ per benchmark, high vs low TIK
- [ ] TIK-human correlation: r = 0.89 verified on actual data
- [ ] Safetywashing claim: backed by Ren et al. 2024 reference
- [ ] Cross-lingual: 6 languages tested, MAD = 0.04

## Statistical Rigor
- [ ] All results have p-values
- [ ] All results have effect sizes (Cohen's d or η²)
- [ ] All results have confidence intervals (95% bootstrap)
- [ ] Multiple comparisons corrected (Bonferroni or FDR)
- [ ] Power analysis reported for human eval

## Reproducibility
- [ ] Random seeds fixed (42) and reported
- [ ] Full prompts for all 5 judges in supplementary
- [ ] Code repository (anonymous) prepared
- [ ] BenchmarkMeta dataset in HuggingFace format
- [ ] All API call logs saved
- [ ] Compute resources documented

## References
- [ ] Fix `arXiv:2501.xxxxx` → actual arXiv IDs or remove
- [ ] Fix `arXiv:2203.xxxxx` (Gursoy et al.)
- [ ] Fix `arXiv:2406.xxxxx` (Chien et al.)
- [ ] Fix `arXiv:2311.xxxxx` (Marks 2023)
- [ ] Fix `arXiv:2502.xxxxx` (Panigrahy & Sharan 2025)
- [ ] Verify all 50+ references are correct
- [ ] No self-citations that break anonymity

## Ethical Requirements
- [ ] IRB approval obtained (number redacted for review)
- [ ] Pre-registration completed (AsPredicted)
- [ ] Informed consent documented
- [ ] Compensation fair ($9.99/27min = $22.2/hr)
- [ ] Ethics statement in paper
- [ ] License specified (CC-BY-SA 4.0)

## Known Weak Points to Strengthen
- [ ] Label circularity: strengthen human validation (N=500, not just r=0.89)
- [ ] Gödelian argument: clearly scoped as "motivation, not proof"
- [ ] Lyapunov: clearly scoped as "analogy, not guarantee"
- [ ] Kernel choice: sensitivity analysis with 9 alternatives
- [ ] Goodhart: demonstrate TIK is necessary but not sufficient

## Supplementary Materials
- [ ] Appendix A: Full Gödelian argument (10 subsections)
- [ ] Appendix B-P: All additional appendices complete
- [ ] Anonymous GitHub/HuggingFace repo linked
- [ ] Code runs end-to-end from scratch
