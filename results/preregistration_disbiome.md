# Pre-registration: Disbiome replication of the BugSigDB literature check (tool 23)
Disclosure: the Disbiome experiment dump (https://disbiome.ugent.be:8080/experiment) was downloaded to a scratch path before this file was written; only its record count (10,866) and field names were inspected. No genus-level counts were computed before this commit.
Question: do keystone-consensus genera appear in more published disease-association experiments than expected from how widespread they are? BugSigDB gave weak, non-robust support (alpha=1 p=0.025; ML alpha p=0.062).
Counts: per genus, number of distinct experiment_id records (primary) and distinct publication_id (secondary). Genus = first word of organism_name, capitalised; names starting "Candidatus", "uncultured", "unclassified" or "[" dropped. Genera from results/keystone_consensus.csv (248), absent = 0.
Model (identical to BugSigDB): NB GLM count ~ kscore (-log10 binomial p) + log(studies modelled); alpha estimated by ML (primary) and fixed at 1 (secondary).
Gate G1: >= 150 of the 248 genera have >= 1 Disbiome experiment.
Pass (D1): ML-alpha kscore coefficient > 0 with two-sided p < 0.05. Otherwise the literature over-representation claim is not supported by Disbiome.
Script: scripts/keystone_disbiome.py; output results/keystone_disbiome.json.
