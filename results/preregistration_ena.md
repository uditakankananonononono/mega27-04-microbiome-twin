# Pre-registration: is the ridge anaerobe-keystone GAI association confounded by genome-sequencing effort? (ENA portal API; tool 27; committed before genus queries; two connectivity checks run: total bacterial assembly count and taxonomy lookup of "Eikenella")
Data: ENA taxonomy REST (scientific-name/<genus>, keep rank = genus with lineage starting "Bacteria" or "Archaea") -> taxId; ENA portal API count?result=assembly&query=tax_tree(<taxId>) -> public assemblies per genus. Cached to results/keystone_ena_counts.csv.
Rival: genera with many sequenced genomes have better-estimated GAI and are also better-characterised keystones; GAI could proxy for sequencing effort.
Model: OLS frac_top ~ GAI + log10(1 + ENA assemblies) + log10(mean relative abundance), HC3 SEs, genera from results/keystone_kegg_genus.csv with GAI.
Gate G1: >= 180 genera resolved to an ENA genus taxId with a count.
Pass (A1): GAI slope > 0 with two-sided p < 0.05 after adjustment. Reported: Spearman(ENA assemblies, KEGG n_genomes); Spearman(frac_top, log assemblies).
Note: this tests only the ridge keystone definition (see the gglasso negative).
Script: scripts/keystone_ena.py; output results/keystone_ena.json.
