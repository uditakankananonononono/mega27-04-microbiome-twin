# Pre-registration: anaerobe-keystone in the IJSEM phenotypic database (Barberan et al. 2017, figshare 4272392); committed before download
Caveat stated in advance: Madin et al. 2020 merged IJSEM records, so this is a re-annotation check, not fully independent.
Test: genus-level anaerobe fraction from IJSEM "Oxygen" field (anaerobic / obligate anaerobe = 1; aerobic, facultative, microaerophilic = 0), mean over species records.
H: Spearman rho(frac_top, IJSEM anaerobe fraction) > 0 across keystone-table genera (results/keystone_kegg_genus.csv), one-sided p < 0.05; and logistic/OLS slope positive after adjusting for log mean abundance (results/keystone_genus_abundance.csv.gz if joinable).
Fail = reported negative.
