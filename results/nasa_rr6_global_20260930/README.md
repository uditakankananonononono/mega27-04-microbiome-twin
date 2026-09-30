# Frozen RR-6 full-panel test: no supported global association

Question: do microbial genus profiles track the host expressed transcriptome within condition and mission-duration groups, beyond shared group shifts?

The colon test uses 34 accepted identity pairs, five strata and 19,857 expressed genes; liver uses 45 pairs, six strata and 16,714 genes. Primary microbial profiles contain 29 genus features from Swift1S. All host genes passing the frozen mean-count/prevalence gate are used, not genes selected for association. The statistic compares within-stratum residual Gram matrices after Hellinger microbial transformation and log1p/standardized host expression. There are 9,999 host-label permutations within strata with seed 20260930.

Primary colon RV is 0.15521, permutation p 0.4345, BH q 0.4345. Primary liver RV is 0.14199, p 0.1039, q 0.2078. Neither passes. NxtaFlex and 16S sensitivities also do not pass. No pathway interpretation or post hoc single-gene search follows. This is a narrow negative under one frozen global statistic, not proof that no host-microbe associations exist. Cohort/identity and cage limitations remain; the data were already partly exposed and this is not untouched validation.

The parent selected a community-to-host pathway route. The frozen first gate is deliberately global expressed-transcriptome association; it is not a curated pathway enrichment analysis. The primary fails, so pathway-specific interpretation is not performed. No new biological discovery, benchmark win or causal effect is credited.

Full source expression tables total 48.9 MB; used only for light numerical analysis, without raw-read downloads, alignments or model training. Complete tested gene IDs and summary rows are included. Reproduce with scripts/nasa_rr6_community_host.py and the source expression directory plus data/nasa_rr6_processed. The source directory can be rebuilt from data/nasa_rr6_host_selected/source_ledger.json's exact download URLs. Gene panels are retained, but the 48.9 MB tables are not duplicated in this repository.

Sources:
- https://osdr.nasa.gov/bio/repo/data/studies/OSD-247
- https://osdr.nasa.gov/bio/repo/data/studies/OSD-245
- https://osdr.nasa.gov/bio/repo/data/studies/OSD-249
- https://www.nature.com/articles/s41522-024-00545-1
