# MDSINE2 healthy cohort: hold-one-mouse-out forecasting (preliminary)
Data: gerberlab/MDSINE2_Paper datasets/gibson/healthy (4 mice with qPCR, 75-77 samples each, 0-64.5 days; high-fat diet, vancomycin, gentamicin perturbations). Top 40 ASVs by mean relative abundance; absolute = relative x mean qPCR.
Metric: RMSE of log10(abundance + 1e5) over all taxa x timepoints (not yet matched to the paper's 141-ASV non-zero-entry metric).
| model | mean RMSE over 4 folds |
|---|---|
| population mean trajectory (other mice, no held-out data) | 1.040 |
| gLV ridge lambda=100 (forecast from t0 + perturbation schedule) | 1.945 |
| growth + perturbation, no interactions | 2.032 |
| persistence (x(t)=x(0)) | 3.048 |
| gLV ridge lambda=0.1/1/10 | 3.68 / 3.38 / 3.09 |
Read: a zero-parameter population-mean trajectory beats every forward-simulated gLV variant by ~2x; interactions add nothing over growth+perturbation. Same pattern as the cNODE benchmark null result.
To do before any claim vs MDSINE2: match the published metric (141 ASVs, non-zero entries, their filtering) and pull MDSINE2's per-fold RMSE from the paper's source data.
