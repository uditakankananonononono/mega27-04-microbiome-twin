# Pre-registration: literature-volume control with an independent index (OpenAlex; tool 30; committed before genus queries; one connectivity check on "Eikenella")
Data: OpenAlex API works?filter=title_and_abstract.search:<genus>&per_page=1 -> meta.count per genus for the 248 genera of results/keystone_consensus.csv. Cached to results/keystone_openalex_counts.csv.
O1 (replication of Europe PMC E1 with a different index): NB (ML alpha) Disbiome n_exp ~ kscore + log(studies modelled) + log(1 + OpenAlex works); pass if kscore coef > 0, two-sided p < 0.05.
O2 (new): same covariate added to the BugSigDB model (n_signatures from results/keystone_bugsigdb.csv); pass if kscore coef > 0, two-sided p < 0.05. BugSigDB without the covariate was weak (ML p = 0.062).
Gate G1: >= 240 genera with a count.
Script: scripts/keystone_openalex.py; output results/keystone_openalex.json.
