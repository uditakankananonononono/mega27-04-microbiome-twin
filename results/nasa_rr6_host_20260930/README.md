# Four prespecified RR-6 same-subject association tests

Metadata establishes 34 accepted fecal-colon pairs and 45 fecal-liver pairs after exact source label and individual-ID agreement. LAR GC10 and ISS-T GC7 are excluded for conflicting identifiers; identifiers were not manually corrected. The colon pairs occupy five source-condition/duration strata; liver pairs occupy six. These are accepted identity pairs, not proof of independent cage-level treatment replication.

Four exploratory tests were frozen before reading expression values: Muc2/Blautia and Ffar2/Intestinimonas in colon; Cyp7a1/Blautia and Nr1h4/Parabacteroides in liver. Primary data use normalized rRNA-removed host expression and Swift1S genus proportions. Correlations use within-stratum centered ranks, with pooled Spearman reported separately. Across the four primary tests, correlations are -0.0100, -0.1402, -0.1696 and -0.0578; approximate independent-sample BH q values are 0.9581, 0.9198, 0.9198 and 0.9581. None supports an association. Correlations and p values are exploratory, not cage-aware causal evidence. Sequencing-assay sensitivities sometimes change direction and do not rescue the result.

This is a narrow negative screen, not proof that host and microbiome biology are unrelated. These host genes/pathways were already discussed in the published RR-6 analysis; no novel pathway or biological discovery is claimed. The successful identity bridge enables further prospectively specified work, but these opened data cannot become untouched validation.

Only four selected expression rows are stored in data/nasa_rr6_host_selected, with original whole-table hashes and download URLs. Reproduce with `python scripts/nasa_rr6_host_associations.py data/nasa_rr6_host_selected data/nasa_rr6_processed results/nasa_rr6_host_20260930`. The same script also accepts the original full source tables. Four grouped artifact sanity checks passed, not a full-suite rerun. No raw-read processing, alignments or model training.

Sources:
- https://osdr.nasa.gov/bio/repo/data/studies/OSD-247
- https://osdr.nasa.gov/bio/repo/data/studies/OSD-245
- https://osdr.nasa.gov/bio/repo/data/studies/OSD-249
- https://www.nature.com/articles/s41522-024-00545-1
Gene-symbol to Ensembl identity was resolved live through MyGene.info, with returned requests/results in data/nasa_rr6_host_selected/gene_ids.json. Ensembl lookup was unavailable during this run, so gene identity uses that alternate source, not recalled identifiers.
