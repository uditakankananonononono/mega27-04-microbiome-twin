# Keystone consensus across MGnify studies (exploratory)
Method: scripts/keystone_mgnify.py. Per study, fit the ridge interaction model (lambda 100) on all samples and build a directed networkx graph (edge j->i weight |W_ij|). Score each genus by weighted out-degree. A genus is "top" if it is in the study's top 10%. Test: binomial vs 10%, BH-FDR over the 248 genera modelled in at least 20 studies.
Result (results/keystone_consensus.csv): 2 of 248 genera pass FDR < 0.05.
- Cardiobacterium: top in 13/30 studies, q = 0.0006
- Eikenella: top in 11/28 studies, q = 0.005
Both are oral HACEK genera, so the signal likely reflects the oral studies, where interaction models fit best. It is not a cross-biome keystone law.
Caveats: out-strength from a ridge model is a statistical dependence score, not a causal keystone effect, and it scales with each genus's variance and prevalence. No experimental validation. Exploratory only.

## Phylogenetic clustering (NCBI Taxonomy; results/keystone_taxonomy.csv, results/keystone_phylum_enrichment.csv)
- 240/248 genera were resolved to a phylum through NCBI Taxonomy E-utilities, restricted to Bacteria/Archaea after 5 eukaryote homonyms (e.g. Bacillus) were caught and fixed.
- Among the 25 lowest-p keystone genera, Thermodesulfobacteriota (sulfate reducers) are enriched: 3/3 (Desulfobulbus, Desulfovibrio, Bilophila), one-sided Fisher p = 0.001, BH q = 0.019 over 19 phyla.
- No other phylum is enriched. Caveat: only 3 genera in this phylum, and none individually passes FDR. Exploratory. A plausible reading is hydrogen/sulfur cross-feeding hubs, but this is a hypothesis, not tested.

## Literature cross-check with BugSigDB (results/keystone_bugsigdb.json, results/keystone_bugsigdb.csv)
- Genus-level signatures: 9,887 published differential-abundance signatures (BugSigDB export 2026-09-24). 236/248 modelled genera appear at least once.
- Negative-binomial GLM, n_signatures ~ keystone score (-log10 p) + log(studies modelled):
  - With alpha fixed at 1: coef 0.20, p = 0.025.
  - With alpha estimated by ML (1.16): coef 0.20, p = 0.062.
  - Marginal Spearman rho = 0.18 (p = 0.004), but this is confounded by how widespread a genus is.
- Verdict: weak, not robust. Keystone-consensus genera are not clearly over-represented in the disease literature once prevalence is controlled. Kept as a negative.

## GTDB replication (scripts/keystone_gtdb.py, results/keystone_gtdb.json, results/keystone_gtdb_phylum_enrichment.csv)
Re-mapped all keystone genera to GTDB release v232 (bac120 taxonomy; 227/248 genera mapped). The sulfate-reducer enrichment replicates under the independent phylogenomic taxonomy: Desulfobacterota 3/3 in top-25, one-sided Fisher p=0.0012, BH q=0.020 (NCBI: Thermodesulfobacteriota q=0.019). NCBI and GTDB disagree on phylum for only 7 genera, mostly naming (Thermodesulfobacteriota vs Desulfobacterota; Mycoplasmatota vs Bacillota). At family level nothing survives FDR (Desulfovibrionaceae 2/2, p=0.012, q=0.71).
Caveat: the result rests on 3 genera (Desulfovibrio, Bilophila, Desulfobulbus), so it is fragile. GTDB replication shows it does not depend on the taxonomy used; it does not add statistical power.

## Physiological traits of keystones: Madin et al. 2020 trait database (scripts/keystone_traits.py, results/keystone_traits_tests.csv, results/keystone_traits_confound.json)
Species traits (14,893 species, condensed_species_NCBI.csv) aggregated to genus; 192-225 of 248 genera have each trait.
- Anaerobe share rises with keystone frequency: Spearman rho=0.30 (p, q = 4e-06 2.8e-05). Top-25 mean anaerobe share 0.70 vs 0.41 (Mann-Whitney p=0.012, q=0.080).
- Smaller genomes: rho=-0.25, q=0.0008. Gram stain, motility, sporulation, GC and doubling time: not significant after BH.
- Confound checks: rank-OLS with genome size and log(study count) keeps anaerobe (p=5.8e-4, HC3) and genome size (p=0.009); permuting anaerobe share within study-count quintiles gives p=2e-4 (5,000 permutations).
Named candidate, not claimed: "anaerobe-keystone hypothesis" - genera with more strictly anaerobic species rank as keystones more often, independent of genome size and study count. Caveat: not controlled for biome (anaerobes dominate gut studies) or abundance. Falsifiable test: the association should hold within single-biome subsets and in an independent cohort. Until then it is a candidate.

### Within-biome falsification test (scripts/keystone_traits_biome.py, results/keystone_traits_biome.json)
- Within-study contrast (top vs non-top genera in the same study, 155 MGnify studies): anaerobe share is higher in keystones in 62% of studies, mean +0.071, sign-flip p=2e-4. This removes between-biome confounding.
- Per biome: positive in 7 of 8 biomes (Insecta -0.026, n=7). Unadjusted p<0.05 in Digestive system (+0.065, n=41), Skin (+0.11), Birds (+0.18). None survive BH across 8 biomes (min q=0.10). Oral, Plants, Fish, Mammals, Insecta: not significant.
Verdict: the anaerobe-keystone association survives the within-study test, so it is not only a gut-vs-environment artifact. It is not robust in any single biome after correction. It stays a named candidate. Remaining untested confound: abundance/prevalence of anaerobes within a study.

### Abundance/prevalence confound (scripts/keystone_traits_abundance.py, results/keystone_traits_abundance.json)
Within-study logistic model with study fixed effects and study-clustered SE (10,599 genus-study rows, 156 studies): top ~ anaerobe + log10 mean relative abundance + prevalence.
Anaerobe coefficient 0.40 (p=1.4e-4), almost unchanged from the model without abundance terms (0.41, p=7e-5). Anaerobe share is barely correlated with abundance (r=0.09) or prevalence (r=-0.02). Keystones are, if anything, less abundant (coef -0.29, p=8e-4) and more prevalent (0.77, p=0.017).
Verdict: the anaerobe-keystone association is not explained by abundance or prevalence. It remains a candidate (named, falsifiable) because (a) per-biome tests are not BH-robust and (b) keystone status comes from our own inferred interaction networks, so it is a property of the inference method until validated with perturbation data.

### Genomic replication with KEGG (scripts/keystone_kegg.py, results/keystone_kegg.json, results/keystone_kegg_genus.csv)
Independent of the Madin phenotype database: marker-KO presence in 11,951 KEGG genomes (rest.kegg.jp link/genes), aggregated to genus (203/248 mapped).
- Validation: genomic anaerobe index GAI = frac(PFOR: K00169|K03737) - frac(coxA: K02274) agrees with Madin anaerobe share (Spearman 0.84).
- Keystone frequency: GAI rho=0.36 (p=9e-8); coxA rho=-0.40 (p=3e-9); PFOR 0.24; [FeFe]-hydrogenase 0.18 (p=0.012); DSR 0.12 (p=0.079).
- Within-study FE logit with abundance + prevalence (13,294 rows, 159 studies, study-clustered SE): GAI coef 0.32, p=7e-8. Split: coxA -0.52 (p=6e-6) carries most of it, PFOR +0.15 (p=0.083). Complete dissimilatory sulfate reduction (dsrA+dsrB+aprA) +0.70, p=3e-5.
Verdict: the anaerobe-keystone candidate replicates with an independent genomic data source and a larger row set; the signal is mainly "lack of aerobic respiration" plus sulfate reduction. Still a candidate: keystone status comes from inferred networks, and no perturbation validation exists.

### Third source: BV-BRC genome metadata (scripts/keystone_bvbrc.py, results/keystone_bvbrc.json)
Oxygen-requirement annotations of 11,323 BV-BRC genomes (facet by genus; genera with >= 3 annotated genomes: 102 of the keystone genera).
Agreement: Spearman 0.83 with Madin, 0.81 with KEGG GAI. Keystone frequency: rho=0.34 (p=5.5e-4). Within-study FE logit with abundance + prevalence (6,804 rows, 151 studies): coef 0.44, p=5.6e-4.
The candidate replicates across three trait sources (phenotype synthesis, KEGG gene content, BV-BRC metadata). They are not fully independent (curated phenotype sources overlap), and none addresses the inference-method caveat.

## Phylogenetic control (PGLS, GTDB bac120 tree) - scripts/keystone_pgls.py, results/keystone_pgls.json
227 keystone-table genera mapped to one representative GTDB bac120 tip each (tree: 189,801 tips). Brownian covariance from root-to-LCA path lengths, Pagel's lambda by ML on a 0..1 grid.
- Keystone fraction has phylogenetic signal: lambda = 0.4, LR test vs lambda=0 p = 0.0042. So species-level non-independence is real and must be controlled.
- PGLS frac_top ~ Madin anaerobe (n=212): lambda_ML=0.2, slope 0.053, p=1.8e-4. Under full Brownian motion (lambda=1): slope 0.048, p=0.097 (NOT significant).
- PGLS frac_top ~ KEGG anaerobic-gene index GAI (n=193): lambda_ML=0.2, slope 0.037, p=4.3e-7; under full Brownian: slope 0.032, p=0.0064.
Verdict: the genomic (GAI) version survives every phylogenetic model tried; the binary Madin-anaerobe version survives at the ML lambda but not under strict Brownian motion. Limits: one tip per genus, grid-search lambda, no genus-level tree uncertainty.

## IJSEM phenotypic database check (pre-registered 142c972; scripts/keystone_ijsem.py, results/keystone_ijsem.json)
150 keystone-table genera matched to IJSEM oxygen preference (anaerobic=1). Spearman rho=0.35, one-sided p=4.4e-6; OLS adjusted for log abundance slope 0.059, HC3 p=6.7e-7 -> PASS.
Caveat: IJSEM is one of the sources merged into Madin et al. 2020 (binary agreement 96.6%), so this confirms the annotation, not an independent replication.
