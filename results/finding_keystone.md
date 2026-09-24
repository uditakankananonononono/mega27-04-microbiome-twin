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
