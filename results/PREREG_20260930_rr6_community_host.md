# RR-6 global community-to-host test, 2026-09-30 10:14 IST

Exploratory extension. Four prior single-gene tests were negative; their rows and all microbiome abundance are exposed. This is not independent validation or untouched discovery.

Question: do full microbial genus profiles track the host's full expressed transcriptome within flight/basal/ground and mission-duration strata, rather than merely matching group shifts?

Two primary tissue tests: colon OSD-247 and liver OSD-245, matched to fecal OSD-249 by Source Name and agreeing trimmed individual source IDs. Use prior accepted mappings (34 colon, 45 liver); do not repair conflicting IDs. Swift1S full genus panel primary. All non-UNKNOWN genus rows retained, renormalize assigned mass, Hellinger transform. Host: NASA normalized rRNA-removed expression; retain all genes with mean count >=10 and nonzero in >=80% of accepted samples, log1p, standardize each gene across accepted samples. This is an expressed transcriptome panel, not a curated pathway label or functional assay.

Center feature values within six/five condition-duration strata. RV statistic: normalized Frobenius product between microbial and host residual Gram matrices. Test with 9999 permutations of host residual sample labels within each stratum, fixed RNG seed 20260930, one-sided statistic, (exceedances+1)/(permutations+1). Apply BH across the two tissue primary tests. Alternate NxtaFlex and 16S are sensitivity tests of the same samples, not independent replication; do not replace a failed primary with a successful alternate. Keep identity/cage limits visible. No causal effect, prediction accuracy, pathway specificity or population independence inferred.

Secondary descriptive tissue-level pathway interpretation is allowed only if the global primary passes and any pathway test is separately frozen before computing it; no post hoc single-gene hunting. A positive primary is an exploratory community/transcriptome association, not an established novel mechanism. A negative primary closes this route.

Compute: ~49 MB existing processed tables, at most 45 samples, feature-by-sample operations and 9999 small Gram permutations per tissue/assay; no model training, alignments or raw-read processing. Bound wall time to two minutes, single-thread numerical libraries. Store complete tested gene IDs, sample mappings, seed, permutations and source hashes. No independent benchmark/discovery gate is credited.
