# Pre-registration: 16S/rRNA sequencing-effort control (RNAcentral via EBI Search; tool 36; committed before genus queries; connectivity checks on "Bacteroides" and "Cardiobacterium" only)
Complements genome-effort controls (ENA tool 27, Ensembl tool 32) with marker-gene effort: many rRNA sequences = well represented in amplicon databases (SILVA/RDP/Greengenes/ENA members of RNAcentral).
Data: EBI Search REST rnacentral?query=<genus> AND rna_type:"rRNA"&size=0 -> hitCount per genus, genera of results/keystone_kegg_genus.csv with GAI. Free-text genus match (noisy). Cached to results/keystone_rnacentral_counts.csv.
Model: OLS frac_top ~ GAI + log10(1 + rRNA sequences) + log10(mean relative abundance), HC3.
Gate G1: >= 180 genera with a count.
Pass (R1): GAI slope > 0, two-sided p < 0.05. Reported: Spearman(rRNA sequences, ENA assemblies); rRNA coefficient.
Ridge keystone definition only.
Script: scripts/keystone_rnacentral.py; output results/keystone_rnacentral.json.
