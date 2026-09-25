# Pre-registration: ProTraits oxygen check of anaerobe-keystone (committed before downloading the data rows; only the header line was read to fix column names)
Data: ProTraits (Brbic et al. 2016, NAR 44:10074), protraits.irb.hr/data/ProTraits_binaryIntegratedPr0.95.txt (integrated text-mining + genome-based predictions at precision >= 0.95). Columns used: Organism_name, oxygenreq=strictanaero.
Coding: per organism, strictanaero call 1 -> 1, 0 -> 0, '?' or blank -> missing. Genus = first word of Organism_name (capitalised; names starting with "Candidatus" or in square brackets dropped). Genus share = mean over organisms with a call.
Genera: results/keystone_kegg_genus.csv (deduplicated genus_clean).
Gate G1: >= 100 genera matched with >= 1 call.
Pass criterion (H1): Spearman rho(frac_top, ProTraits anaerobe share) > 0 with one-sided p < 0.05 AND OLS frac_top ~ share + log10(mean relative abundance) slope > 0 with HC3 two-sided p < 0.05.
Reported (not gates): agreement with KEGG GAI (Spearman) and Madin binary anaerobe (fraction agreeing at 0.5).
Independence caveat stated in advance: ProTraits text mining draws on literature that also feeds Madin et al. 2020; the genome-based predictors are closer to KEGG gene content. This is a partly independent annotation check, not a new cohort.
Script: scripts/keystone_protraits.py; output results/keystone_protraits.json.
