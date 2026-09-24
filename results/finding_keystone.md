# Keystone consensus across MGnify studies (exploratory)
Method: scripts/keystone_mgnify.py. Per study, fit the ridge interaction model (lambda 100) on all samples and build a directed networkx graph (edge j->i weight |W_ij|). Score each genus by weighted out-degree. A genus is "top" if it is in the study's top 10%. Test: binomial vs 10%, BH-FDR over the 248 genera modelled in at least 20 studies.
Result (results/keystone_consensus.csv): 2 of 248 genera pass FDR < 0.05.
- Cardiobacterium: top in 13/30 studies, q = 0.0006
- Eikenella: top in 11/28 studies, q = 0.005
Both are oral HACEK genera, so the signal likely reflects the oral studies, where interaction models fit best. It is not a cross-biome keystone law.
Caveats: out-strength from a ridge model is a statistical dependence score, not a causal keystone effect, and it scales with each genus's variance and prevalence. No experimental validation. Exploratory only.

## Phylogenetic clustering (NCBI Taxonomy; results/keystone_taxonomy.csv, results/keystone_phylum_enrichment.csv)
- 240/248 genera were resolved to a phylum through NCBI Taxonomy E-utilities, restricted to Bacteria/Archaea after 5 eukaryote homonyms (e.g. Bacillus) were caught and fixed.
- Among the 25 lowest-p keystone genera, Thermodesulfobacteriota (sulfate reducers) are enriched: 3/3 (Desulfobulbus, Desulfovibrio, Bilophila), one-sided Fisher p = 0.001, BH q = 0.019 over 19 phyla.
- No other phylum is enriched. Caveat: only 3 genera in this phylum, and none individually passes FDR. Exploratory. A plausible reading is hydrogen/sulfur cross-feeding hubs, but this is a hypothesis, not tested.

## Literature cross-check with BugSigDB (results/keystone_bugsigdb.json, results/keystone_bugsigdb.csv)
- Genus-level signatures: 9,887 published differential-abundance signatures (BugSigDB export 2026-09-24). 236/248 modelled genera appear at least once.
- Negative-binomial GLM, n_signatures ~ keystone score (-log10 p) + log(studies modelled):
  - With alpha fixed at 1: coef 0.20, p = 0.025.
  - With alpha estimated by ML (1.16): coef 0.20, p = 0.062.
  - Marginal Spearman rho = 0.18 (p = 0.004), but this is confounded by how widespread a genus is.
- Verdict: weak, not robust. Keystone-consensus genera are not clearly over-represented in the disease literature once prevalence is controlled. Kept as a negative.

## GTDB replication (scripts/keystone_gtdb.py, results/keystone_gtdb.json, results/keystone_gtdb_phylum_enrichment.csv)
Re-mapped all keystone genera to GTDB release v232 (bac120 taxonomy; 227/248 genera mapped). The sulfate-reducer enrichment replicates under the independent phylogenomic taxonomy: Desulfobacterota 3/3 in top-25, one-sided Fisher p=0.0012, BH q=0.020 (NCBI: Thermodesulfobacteriota q=0.019). NCBI and GTDB disagree on phylum for only 7 genera, mostly naming (Thermodesulfobacteriota vs Desulfobacterota; Mycoplasmatota vs Bacillota). At family level nothing survives FDR (Desulfovibrionaceae 2/2, p=0.012, q=0.71).
Caveat: the result rests on 3 genera (Desulfovibrio, Bilophila, Desulfobulbus), so it is fragile. GTDB replication shows it does not depend on the taxonomy used; it does not add statistical power.
