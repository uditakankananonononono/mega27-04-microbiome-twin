# Pre-registration: InterPro replication of the genomic anaerobe index (tool 34; committed before genus queries; connectivity checks on taxIds 816 and 2717 only)
Data: InterPro API protein/uniprot/taxonomy/uniprot/<taxId>/entry/interpro/<IPR>?page_size=1 -> count (HTTP 204 = 0), per genus NCBI taxId from results/keystone_ena_counts.csv:
 n_pfor = IPR011895 (pyruvate-flavodoxin oxidoreductase family); n_cox = IPR000883 (cytochrome c oxidase subunit I); n_recA = IPR013765 (RecA family, normaliser).
Index IGAI = min(1, n_pfor / n_recA) - min(1, n_cox / n_recA), genera with n_recA >= 1. Cached incrementally to results/keystone_interpro_counts.csv (the script is re-run with a time budget until all genera are fetched; failed calls stay missing and are retried on the next run).
Note: IPR000883 covers haem-copper oxidase subunit I broadly (includes non-aa3 oxidases), unlike EC 7.1.1.9 in tool 29.
Gate G1 (validity): >= 150 genera with n_recA >= 1 and Spearman(IGAI, KEGG GAI) >= 0.6.
Pass (P1): OLS frac_top ~ IGAI + log10(mean relative abundance), HC3, IGAI slope > 0, two-sided p < 0.05.
Caveat: InterPro protein sets are UniProtKB, overlapping with tool 29; this replicates with signature-based (InterProScan member database) annotation rather than EC rules. Ridge keystone definition only.
Script: scripts/keystone_interpro.py; output results/keystone_interpro.json.
