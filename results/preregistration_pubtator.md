# Pre-registration: independent replication of the oral-hub effect with a literature-derived oral index (NCBI PubTator3 API; tool 38; committed before genus queries; syntax check on "Eikenella" only)
HOMD is a curated binary list; this uses a continuous, independent index.
Data: PubTator3 search count for text "<genus>" (n_all) and "<genus> AND (oral OR dental)" (n_oral) for every genus in the gglasso/igraph model rows (KEGG genera with GAI). Oral literature fraction OLF = n_oral / n_all (genera with n_all >= 5; else missing). Cached to results/keystone_pubtator_counts.csv.
Model: as scripts/keystone_methodgeneral.py but with OLF (standardised z-score) in place of HOMD oral: logit top ~ OLF_z + GAI + lra + prevalence + C(study), SE clustered by study, for gglasso and igraph labels.
Gate G1: >= 180 genera with OLF.
Pass (PT1): OLF_z coefficient > 0, two-sided p < 0.05 under BOTH gglasso and igraph. Reported: Spearman(OLF, HOMD oral), ridge arm.
Script: scripts/keystone_pubtator.py; output results/keystone_pubtator.json.
