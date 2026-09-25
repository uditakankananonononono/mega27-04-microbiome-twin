# Pre-registration: is the anaerobe-keystone association an oral-taxon artefact? (expanded Human Oral Microbiome Database, HOMD; tool 35; committed before the taxon table download; only the site index/file listing was viewed)
Rival: top keystones include oral genera (Cardiobacterium, Eikenella); oral-gut translocation is disease-linked and many oral taxa are anaerobes, so "oral origin" could drive the GAI association.
Data: https://www.homd.org/ftp/taxonomy/HOMD_taxon_table_v4.2.csv. Genus column = first column whose header contains "genus" (case-insensitive). If a column whose header contains "site" exists, oral = genus has >= 1 row whose site text contains "oral" (case-insensitive); otherwise oral = genus present in the table. Cached to data/ref/HOMD_taxon_table_v4.2.csv.
Model: OLS frac_top ~ GAI + oral + log10(mean relative abundance), HC3, genera of results/keystone_kegg_genus.csv with GAI.
Gate G1: >= 20 GAI genera classed oral.
Pass (M1): GAI slope > 0, two-sided p < 0.05 with the oral covariate. Secondary (reported, not gates): oral coefficient; GAI slope on non-oral genera only.
Ridge keystone definition only.
Script: scripts/keystone_homd.py; output results/keystone_homd.json.
