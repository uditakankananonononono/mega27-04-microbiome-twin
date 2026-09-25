# Pre-registration: is the Disbiome keystone-literature link study bias? (Europe PMC; tool 24; committed before any genus queries except one connectivity test on "Eikenella")
Data: Europe PMC REST search API, hitCount for query TITLE_ABS:"<genus>" per genus in results/keystone_consensus.csv (248 genera), cached to results/keystone_europepmc_counts.csv.
Rival R: keystone-consensus genera are simply more studied; the Disbiome (and BugSigDB) excess reflects literature volume, not disease relevance.
Model: NB (alpha by ML) Disbiome n_exp ~ kscore + log(studies modelled) + log(1 + Europe PMC hits). Also reported: Spearman(kscore, log hits).
Pass (E1): kscore coefficient > 0 with two-sided p < 0.05 after adding the literature covariate -> the Disbiome link is not explained by literature volume. Fail -> R supported; the literature link is recorded as study bias.
Gate G1: >= 240 genera return a hitCount (API success).
Script: scripts/keystone_europepmc.py; output results/keystone_europepmc.json.
