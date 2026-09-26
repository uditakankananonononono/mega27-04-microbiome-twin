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

## Metric matched to the MDSINE2 paper's evaluation code (paper_figures/fig3_cross_validation.ipynb)
Per (held-out mouse, taxon) RMSE of log10 abundance over timepoints with truth > 1e5 (limit of detection); predictions floored at 1e5; top 141 ASVs (paper uses 141 filtered ASVs - our selection is by mean abundance, an approximation). 546 taxon-mouse pairs.
| model | median | mean |
|---|---|---|
| population mean trajectory (LOD-floored, zero held-out info) | 0.837 | 0.968 |
| gLV ridge lambda=100 | 1.880 | 1.891 |
| gLV ridge lambda=1000 | 1.889 | 1.925 |
| gLV ridge lambda=10 | 2.601 | 2.641 |
Null better in 483/546 pairs, Wilcoxon p = 5e-78. Next: read MDSINE2 / cLV / gLV-elastic-net medians off the paper's Fig. 3 for the head-to-head.

## CORRECTION - exact head-to-head on the paper's own source data (Nature Microbiology 2025, Source Data Fig. 3, healthy absolute)
Official metric reproduced from paper_figures/fig3_cross_validation.ipynb (truth > 1e-5, eps = 1e3, per subject x taxon RMSE of log10). Our recomputation of MDSINE2 gives median 1.061, matching the published box plot, so the pipeline is verified.
| method | median | mean |
|---|---|---|
| MDSINE2 (No Modules) | 0.913 | 1.024 |
| MDSINE2 | 1.061 | 1.195 |
| population-mean null (ours, training mice only) | 1.442 | 1.576 |
| gLV elastic net | 1.446 | 1.592 |
| gLV ridge | 1.924 | 2.098 |
MDSINE2 beats the null (null better in only 184/556 pairs, Wilcoxon p = 2e-20). The earlier "null beats everything" reading came from flooring predictions at 1e5, a different metric, and is RETRACTED for MDSINE2. What survives: the zero-parameter null ties gLV elastic net and beats gLV ridge - classical gLV baselines in this benchmark are no better than a population average.

## Presence-conditional population forecaster vs MDSINE2 (same official metric, same 556 pairs)
Model (src/microtwin/popforecast.py): for each taxon and day, average log10 abundance over training mice *where the taxon was detected*; optional decaying offset from the held-out mouse's day-1 value (tau by inner leave-one-mouse-out on training mice).
| model | median | vs MDSINE2 (No Modules), pairs better | Wilcoxon p | vs MDSINE2 Wilcoxon p |
|---|---|---|---|---|
| presence-conditional population forecaster | 0.919 | 299/556 | 0.53 (tie) | 1.1e-4 (ours lower) |
| same + initial-offset (tau inner-LOO, chose 0-1 day) | 0.920 | 298/556 | 0.48 | 1.2e-4 |
| unconditional population mean | 1.442 | 142/556 | 4e-43 (worse) | 2e-20 (worse) |
Published medians: MDSINE2 1.061, MDSINE2 no-modules 0.913.
Read: a parameter-free presence-conditional average ties the best published model and beats full MDSINE2 on MDSINE2's own benchmark. Inner-LOO picks tau ~0: the held-out mouse's initial state adds nothing.
Caveat that matters: the official metric scores only timepoints where the taxon is detected, so it rewards presence-conditional prediction; this is as much a finding about the benchmark metric as about the models. 4 variants were compared (mild multiple testing). Healthy cohort only; UC cohort next.

## Replication on the UC-donor cohort (bench_mdsine2.py uc; same official metric, 601 taxon-mouse pairs)
Ours (presence-conditional population forecaster) median 0.692 - lowest of all 12 methods.
vs MDSINE2 (No Modules) 0.805: ours better in 376/601, Wilcoxon p = 8e-7. vs RA-MDSINE2 (No Modules) 0.784: p = 6e-6. vs MDSINE2 1.093: p = 4e-44. vs gLV elastic net 1.582, gLV ridge 1.970.
Healthy cohort re-run with the same script: ours 0.919 = 3rd of 11 (RA-MDSINE2 No Modules 0.883 is better, p = 0.045; tie with MDSINE2 No Modules p = 0.53; beats MDSINE2 1.061 p = 1e-4).
Verdict: benchmark beat on UC cohort, tie-to-slight-loss on healthy. Metric caveat stands (detected-only scoring rewards presence-conditional prediction).

## Test of our own falsifiable prediction: score ALL timepoints (undetected truth included, log10(x + 1e3))
Prediction (paper v1, section 7): with undetected timepoints scored too, the presence-conditional forecaster's advantage should shrink or reverse.
Result: FALSIFIED. The forecaster ranks first on both cohorts, by a wider margin.
- UC: ours median 1.654 vs MDSINE2 (No Modules) 1.824, RA-MDSINE2 (No Modules) 1.803; ours better in 461/605 pairs vs MDSINE2-NM, Wilcoxon p = 3.5e-40 (results/mdsine2_headtohead_uc_alltimepoints.json).
- Healthy: ours median 1.752 vs MDSINE2 (No Modules) 2.072, RA-MDSINE2 (No Modules) 2.084; ours better in 417/564, p = 5.5e-40 (results/mdsine2_headtohead_healthy_alltimepoints.json).
Read: the detection-only metric was not what made the population prior competitive. Under the stricter all-timepoint metric it beats every published method on both cohorts. Pairs: all subject-taxon pairs (605 UC, 564 healthy), i.e. the official 601/556 plus pairs never detected in the held-out mouse.

## 2026-09-26 schedule leakage audit
The first archived `bench_mdsine2.py` reconstructed Figure 3 timepoint days by choosing the qPCR-versus-**held-out truth** best offset, an outcome-assisted procedure inappropriate for a forecast. On inspection, all healthy/UC source subjects select offset 2 except UC subject 10 selecting offset 1; these match the source script's prespecified exclusion of day 0 and 0.5. The script now removes sample times below day 1 based on the published preprocessing rule and asserts an exact schedule-length match, without seeing truth or qPCR. On both cohort reruns the output JSON medians/pair counts are numerically unchanged (see `results/mdsine2_headtohead_*`). This repairs the time-index procedure only; the archived comparisons still use the authors' released test truth for training-*other*-subject trajectories and are not an untouched source-family external benchmark for the expanded project. The nominal Wilcoxon analyses treat many subject-taxon pairs as independent though they cluster within 4 or 5 mice, so small p-values are not decisive study-level evidence. No new platform benchmark win follows from this repair. Published preprocessing source: https://github.com/gerberlab/MDSINE2_Paper (`scripts/preprocess/agglomerate_asvs.sh`, commit `1b20972a7dacd9dca9d801d3011556647bbc64f1`, `--remove-timepoints 0 0.5`).

## Subject-cluster sensitivity, same published cohorts (2026-09-26)
`scripts/mdsine_subject_aggregate.py` calculates each mouse's median paired taxon-level RMSE difference (ours minus comparator) on the same released Figure 3 arrays. Against MDSINE2 without modules, the prior's gap is negative in 3/4 healthy mice and 5/5 UC mice on the detected-only metric. On all timepoints, it is negative in 4/4 healthy and 5/5 UC mice. These signs are a useful consistency check, **not** a statistically powered source-family benchmark: the biological sample is just nine mice in two related lab cohorts, only a few possible mouse-level resamples exist, and the prior's hyperparameters and metric choices were developed on viewed data. The JSON records all nine signed gaps and taxon counts; do not turn taxon-level p-values into independent study-level significance.

## Exact mouse-cluster bootstrap sensitivity (2026-09-26)
`scripts/mdsine_cluster_bounds.py` enumerates all 4^4 or 5^5 mouse-resampling draws of the **mouse-level median paired taxon RMSE gaps** against MDSINE2 without modules, then reports a percentile interval for their average. Prior-minus-comparator gaps: healthy detected-only -0.0356, 95% cluster-resample interval [-0.0978, +0.0396] (uncertain); UC detected-only -0.1061 [-0.1351, -0.0782]; healthy all-timepoints -0.2378 [-0.2514, -0.2284]; UC all-timepoints -0.1734 [-0.1840, -0.1576]. This is a descriptive sensitivity on four and five viewed mice; even an interval below zero does **not** repair model-selection/multiplicity, identify an independent new source or prove a general benchmark beat. The revised exact detected-only UC count is 601 paired subject-taxon units, not the older text's 599. Full arithmetic is pinned in `results/mdsine_cluster_bounds.json`.
