# Keystone consensus across MGnify studies (exploratory)
Method: scripts/keystone_mgnify.py. Per study, fit the ridge interaction model (lambda 100) on all samples and build a directed networkx graph (edge j->i weight |W_ij|). Score each genus by weighted out-degree. A genus is "top" if it is in the study's top 10%. Test: binomial vs 10%, BH-FDR over the 248 genera modelled in at least 20 studies.
Result (results/keystone_consensus.csv): 2 of 248 genera pass FDR < 0.05.
- Cardiobacterium: top in 13/30 studies, q = 0.0006
- Eikenella: top in 11/28 studies, q = 0.005
Both are oral HACEK genera, so the signal likely reflects the oral studies, where interaction models fit best. It is not a cross-biome keystone law.
Caveats: out-strength from a ridge model is a statistical dependence score, not a causal keystone effect, and it scales with each genus's variance and prevalence. No experimental validation. Exploratory only.
