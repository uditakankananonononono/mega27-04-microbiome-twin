# Pre-registration: change of direction - is any keystone correlate method-general? (committed before any model on gglasso/igraph labels with the oral covariate)
Context: the GAI association failed under gglasso (tool 25) and igraph betweenness (tool 31), so it is ridge-specific. HOMD (tool 35) showed oral genera have higher ridge keystone fraction (post-hoc observation at genus level). The oral effect has NOT been examined on gglasso or igraph labels.
Data: per-study labels results/keystone_per_study.csv.gz (ridge top), results/keystone_gglasso_per_study.csv.gz (top_gl), results/keystone_igraph_per_study.csv.gz (top_gl = betweenness top); abundance/prevalence results/keystone_genus_abundance.csv.gz; GAI results/keystone_kegg_genus.csv (merge on genus); oral = genus_clean in HOMD v4.2 oral genera (scripts/keystone_homd.py oral_genera).
Model per method: logit top ~ oral + GAI + log10(mean_ra + 1e-6) + prevalence + C(study), SE clustered by study; studies with no top rows dropped.
Primary (MG1): oral coefficient > 0 with two-sided p < 0.05 under BOTH gglasso and igraph (new tests). Ridge arm reported but not a test (the oral effect there was seen before registration).
Reported: GAI coefficient per method; oral coefficient per method.
If MG1 fails, recorded; the direction changes again (next candidate: prevalence-controlled abundance-rank correlates).
Script: scripts/keystone_methodgeneral.py; output results/keystone_methodgeneral.json.
