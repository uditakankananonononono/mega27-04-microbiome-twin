# First-period SCFA development forecast

Frozen protocol f8a2d63. CC BY 4.0 deposit https://zenodo.org/records/15363886, original study https://pmc.ncbi.nlm.nih.gov/articles/PMC13084677/ . Not a new independently replicated biological discovery or a taxonomic digital twin.

Out of 110 completers with nominal first-period pairs, 84 passed the frozen rules (42/arm): 25 excluded by assay complete-case validity and one by collection-date interval. QC duplicates excluded. No second-period outcomes or GitHub taxonomic values used. Units are measured micrograms/g stool, not compositional taxa. Concentration and metadata inputs verified against deposit hashes. Dataset now exposed development, not an untouched holdout.

| Forecast | Mean standardized absolute log1p error | Mean absolute log1p error |
|---|---:|---:|
| Fixed baseline/arm-interaction ridge | 0.702517 | 0.446566 |
| Persistence | 0.798983 | 0.494623 |
| Same-arm mean delta | 0.806896 | 0.502086 |
| Nearest-three same-arm delta | 0.775684 | 0.497015 |

Relative improvements are 12.07%, 12.94%, 9.43% respectively. Paired model-minus-reference subject-bootstrap 95% intervals are [-0.169426,-0.022469], [-0.172099,-0.034693], [-0.123910,-0.020608]. All are negative but the nearest-three improvement misses the frozen 10% threshold: **useful_win=False**. No threshold relaxed or alternate fit tried. Hexanoic acid log error is 0.690508 for ridge versus 0.601259 for persistence; aggregate improvement does not imply every metabolite improves. Bootstrap is within-study descriptive, not independent-source generalization or calibrated coverage.

Five subject folds scored every eligible submitted subject once; no subject in its training fold. Target replacement left forecasts unchanged; all predictions finite. Evaluation took 0.287 seconds. Execution deviation: target-replacement invariance necessarily refit all five folds, so ten fits occurred (five scoring + five verification), rather than the brief parent plan's five total fits; frozen protocol required the check, all compute remained single-thread and far below 120 seconds. No repeated scientific variants or paid resources.

Only aggregate metrics/metadata receipts are public. Local inputs are re-fetchable from Zenodo and not committed; no sample IDs, participant age/BMI/weights, clinical rows or per-subject errors published. Censoring/complete-case selection restricts applicability. Diet start and adherence are not measured by these metadata. First-period means avoid known later-date anomalies; they do not establish exact perturbation timing or counterfactual effects. No antibiotic validation, independent benchmark beat, reliability, replication or novelty gate closed.
