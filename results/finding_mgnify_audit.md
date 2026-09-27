# Interaction audit across 160 MGnify studies (accessions in data/raw/mgnify/manifest.csv)
Task: predict each sample's genus composition from which genera are present. Presence-conditional two-way prior (log p_si = mu_i + c_s) vs a steady-state gLV-form interaction model (ridge, lambda by inner CV). 5-fold CV, median Bray-Curtis, paired Wilcoxon per study, BH-FDR across studies. Caps: 400 samples, top 150 genera by prevalence.
Code: src/microtwin/audit.py (unit tests: planted interaction detected; no gain on interaction-free data), scripts/audit_mgnify.py, scripts/summarise_audit.py.

## Result (results/mgnify_audit_summary.json, results/mgnify_audit_fdr.csv)
- Interactions better at FDR < 0.05 in 121/160 studies, prior better in 6, no difference in 33.
- Median gain 0.052 BC. Median relative gain 14.5%.
- Every biome has a majority of interaction wins except human digestive system (21/41).
- Relative gain grows with sample count (log n coefficient +0.032, p = 0.006) and with how hard the prior finds the study (prior BC coefficient +0.30, p = 0.002).

## Candidate "human gut is least interaction-predictable": NOT SUPPORTED (confounded)
The gut studies have lower relative gain (median 0.025 vs 0.192, Mann-Whitney p = 3e-11; OLS gut coefficient -0.094, p = 0.001 adjusting for n, taxa and prior BC).
But 33 of 41 gut studies are MGnify metagenome assemblies (SSU from assembled contigs), compared with 2 of 118 non-gut studies.
The 8 non-assembly gut studies show a median relative gain of 0.210, the same as other biomes (0.184).
Gut and data type cannot be separated here. The apparent gut effect is most likely an assembly-data artefact.
Next test: fetch amplicon-only human gut studies and re-run.

## Relation to the cNODE result
On cNODE's human gut and oral tables, the arithmetic-mean presence null matched published cNODE. Here, with a calibrated two-way prior and a linear interaction model, interactions help in most amplicon studies, including oral (17/20).
The two results are not contradictory, because the models, metrics and data differ. But the broad claim "interactions add nothing on human data" is NOT supported by this larger audit.

## Correction 2026-09-27 12:45 IST
The historical 2/118 non-gut assembly denominator above was internally inconsistent with 160 total and is not reproducible with the frozen narrow assembly-phrase rule. The rule flags 33/41 digestive and 0/119 outside digestive; it cannot classify the other 127 as amplicon. A broad `assembl` substring catches four outside digestive but two refer to assemblages/community assembly in another sense. The earlier 0.184 "other biomes" median is also not reproduced by the frozen audit table: non-digestive median finite relative gain is 0.192. The eight title-unflagged digestive tables have gain 0.210 and 8/8 original BH interaction wins, but their assay and independent source-family units are not certified. The phrase "most likely an assembly-data artefact" was too strong: assay, biome, pipeline and source family are entangled. Original wording remains above as dated audit history, not a current conclusion. See `results/mgnify_assay_descriptive.json` and its pre-result protocol.
