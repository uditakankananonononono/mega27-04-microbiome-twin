# Baseline-conditioned ridge: mixed development result, useful-win failure

Frozen plan 6557531, single approved execution, 24 Ridge(alpha=10, SVD) fits, 256 inputs and 255 species, one CPU/BLAS thread. Fit/evaluation elapsed 0.10 seconds, not a promise of future runtime. No second execution, tuning or graph-network training. Baseline log1p(1000*PRE proportion), training-fold standardization and submitted group indicator predict DURING-PRE; outputs clipped and normalized. Held-out outcome exclusion and training-preprocessing checks pass. No POST/recovery labels.

Mean BC error: ridge 0.6435, persistence 0.5351, projected same-group median delta 0.5316, projected nearest-three delta 0.5643. Ridge-minus-reference means and subject-bootstrap intervals are +0.10845 [0.04659,0.18216], +0.11191 [0.05150,0.18102], and +0.07924 [0.02477,0.14959]. Each primary useful-win condition fails; lower error than persistence in only 7/24 subjects. Case/Control group summaries both retain the error disadvantage, with unverified drug meaning.

Secondary zero-wrong direction accuracy is 63.07%, above group median 61.63%, nearest-three 56.95%, decline-only 55.88%. Coverage 96.81%. Secondary direction criterion passes, but no useful development win because the composition-error criteria fail. Correct signs do not imply correct magnitudes. This is a mixed result, not a benchmark beat or biological discovery. No causal/generalization claim follows from submitted-group bootstrap intervals or repeated development work.

Identifiability limit: single transition type, stage conditioning is task selection only. The model is baseline-conditioned but does not estimate different stage/drug effects. Exposed NUH data cannot become untouched validation. Untouched-source criteria in the plan are conditional future requirements, not authorization to hunt or score more cohorts. No external validation expansion is credited from this failure.

Source: https://raw.githubusercontent.com/CSB5/Recovery_Determinants_Study/d374f5e7c09da659d407af5664604b81451c5df4/Data/NUH_StoolSamples_MetaPhlAn2.txt
