# Pre-registration: sequencing-effort control with a second genome archive (EBI Search over Ensembl Genomes / Ensembl Bacteria; tool 32; committed before genus queries; connectivity checks on "Bacteroides" and "Cardiobacterium")
Replication of ENA A1 (tool 27) with Ensembl Bacteria, a curated subset of genomes, instead of all ENA assemblies.
Data: EBI Search REST ensemblGenomes_genome?query=<genus>&size=0 -> hitCount per genus for genera of results/keystone_kegg_genus.csv with GAI. Cached to results/keystone_ensembl_counts.csv. Free-text query, so counts are a noisy proxy.
Model: OLS frac_top ~ GAI + log10(1 + Ensembl genomes) + log10(mean relative abundance), HC3 SEs (same as scripts/keystone_ena.py).
Gate G1: >= 180 genera with a count.
Pass (S1): GAI slope > 0, two-sided p < 0.05. Reported: Spearman(Ensembl genomes, ENA assemblies).
Ridge keystone definition only (gglasso and igraph negatives).
Script: scripts/keystone_ensembl.py; output results/keystone_ensembl.json.
