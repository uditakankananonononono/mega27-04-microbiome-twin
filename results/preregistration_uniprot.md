# Pre-registration: UniProt replication of the genomic anaerobe index (tool 29; committed before genus queries; one connectivity check on Eikenella counts)
Data: UniProt REST uniprotkb/search (size=0, X-Total-Results) restricted to reference-proteome entries (keyword KW-1185), per genus NCBI taxId (from results/keystone_ena_counts.csv):
 n_cox = entries with EC 7.1.1.9 (cytochrome-c oxidase); n_pfor = entries with EC 1.2.7.1 (pyruvate:ferredoxin oxidoreductase); n_recA = entries with gene_exact:recA (single-copy normaliser).
UniProt anaerobe index UGAI = min(1, n_pfor / n_recA) - min(1, n_cox / n_recA), for genera with n_recA >= 1. Cached to results/keystone_uniprot_counts.csv.
Gate G1 (validity): >= 150 genera with n_recA >= 1 and Spearman(UGAI, KEGG GAI) >= 0.6.
Pass (U1): OLS frac_top ~ UGAI + log10(mean relative abundance), HC3, UGAI slope > 0 with two-sided p < 0.05; plus Spearman(frac_top, UGAI) reported.
Caveat stated in advance: UniProt reference proteomes and KEGG genomes overlap heavily (both from RefSeq/ENA assemblies); EC annotation pipelines differ (UniRule/ARBA vs KOfam), so this is an annotation-pipeline replication, not a new-genome replication. Ridge keystone definition only.
Script: scripts/keystone_uniprot.py; output results/keystone_uniprot.json.
