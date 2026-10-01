# Small-n ciprofloxacin direction check

Original PLOS Dataset S3 passed processed-download, open exact course/day mapping, and subject-grouping checks. Frozen local protocol commit 28e6cba preceded opening abundance cells. Source hash, all subject results and an outcome-invariance test are in JSON. The assay contains normalized V3 refOTU abundances; every selected column sums to 43,405 before proportion normalization. Not absolute bacterial load.

Across three leave-one-subject-out day -1 to +5 checks, median-other-two predicts 55.32% macro direction accuracy, nearest pretreatment donor 56.30%, and fixed decline-only reference 66.95%. Observed nearest gain over median is +0.98 percentage points, with mixed subject results. Both donor baselines lose to decline-only. Zero predictions count wrong; no misleading conditional-coverage leaderboard. There are 75, 74 and 94 eligible OTUs for A, B and C respectively, and these are features within three subjects, not 243 independent trials. No bootstrap/significance claim.

Limits: 3 subjects, no untreated controls, OTU-level not validated species, same source family as PNAS. This is a small-n prospective direction check, not a general antibiotic-response claim. It validates an evaluation route, not the platform interaction model. Neither novel discovery, strongest-tool beat nor causal perturbation gate is credited. Public findings had already been read, so no certified untouched-holdout claim. Parent-relayed exposure scan found no relevant tracked text/listing hits, but excluded binary/archive contents and files over 20MB; absence cannot prove no past opening.

Run scripts/plos_cipro_direction.py against the original Dataset S3 XLS. Uses only A2c/B2/C2 and A3b/B3/C3, no recovery samples or published response annotations. A test replacing each held-out outcome with arbitrary values confirms its predictions are unchanged. Inputs remain private; no participant clinical tables republished.

Sources:
- https://journals.plos.org/plosbiology/article?id=10.1371%2Fjournal.pbio.0060280
- https://journals.plos.org/plosbiology/article/file?type=supplementary&id=10.1371/journal.pbio.0060280.sd003
- https://journals.plos.org/plosbiology/article/figure/image?download&size=large&id=10.1371/journal.pbio.0060280.t001
