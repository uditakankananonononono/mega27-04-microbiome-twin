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

## Rival test: genome streamlining (pre-registered 66d7f05; scripts/keystone_genomesize.py, results/keystone_genomesize.json)
NCBI Datasets v2 reference genomes (2,081 genomes, 190 genera; median size and GC per genus). GAI and log genome size correlate (Spearman -0.46).
- Size/GC/abundance alone: R^2 0.043, log size slope -0.041, p=0.10.
- Full model: GAI slope 0.028, HC3 p=1.3e-6; log size p=0.33; GC p=0.34 -> anaerobe association PASSES; the streamlining rival is not supported.

## Independent phylogeny: Open Tree of Life (pre-registered ce6fd94; scripts/keystone_otol.py, results/keystone_otol.json)
TNRS matched 201 of 203 GAI genera to OTT genus ids; 161 are tips in the induced synthetic subtree (the rest are collapsed into unnamed MRCA nodes and dropped). Grafen branch lengths (the synthesis tree has none).
- Pagel lambda of keystone fraction: 0.45, LR vs 0 p = 0.052 (weaker signal than on GTDB).
- PGLS frac_top ~ GAI under full Brownian: slope 0.028, p = 0.017 -> pre-registered H1 PASS. At lambda_ML = 0.3: slope 0.045, p = 9.9e-08.
Verdict: the genomic anaerobe association survives a second, independently built phylogeny. Limits: topology only (Grafen lengths), 161 genera.

## ProTraits oxygen check (pre-registered 4f748be; scripts/keystone_protraits.py, results/keystone_protraits.json) - GATE FAILED
Only 51 keystone-table genera have a strict-anaerobe call at ProTraits precision >= 0.95 (gate: 100), so the pre-registered test fails at the gate. On those genera: Spearman rho = 0.057 (one-sided p = 0.35); abundance-adjusted slope 0.011 (HC3 p = 0.58). ProTraits agrees with Madin on all 51 (binary) and with KEGG GAI at rho = 0.70.
Verdict: uninformative (underpowered, gate failed) and recorded as a negative. The high-confidence ProTraits subset shows no association; we do not re-run at a lower precision threshold without a new pre-registration.

## Disbiome literature check (pre-registered 899f554; scripts/keystone_disbiome.py, results/keystone_disbiome.json)
Disclosure: the dump was downloaded before the pre-registration; only field names and record count were inspected before commit.
10866 disease-association experiments; 203/248 keystone-table genera present. Same NB model as BugSigDB (count ~ kscore + log studies modelled).
- ML alpha (1.60): kscore coef 0.30, p = 0.024 -> pre-registered D1 PASS. Alpha=1: p = 0.0011. Distinct publications: p = 0.018.
Verdict: a second, independent literature database supports modest over-representation of keystone-consensus genera in disease reports, beyond how widespread they are. With BugSigDB (ML p = 0.062) the literature link is now borderline-supported rather than a clear negative; the effect is small and could reflect oral/HACEK disease literature (Cardiobacterium 13, Eikenella 15 experiments).

## Study-bias control with Europe PMC (pre-registered 0358299; scripts/keystone_europepmc.py, results/keystone_europepmc.json)
Europe PMC title/abstract hit counts for all 248 genera (the counts were fetched with the script's own hits() function in 8 parallel threads after a sequential run hit the time limit; cache: results/keystone_europepmc_counts.csv).
Keystone score is not correlated with literature volume (Spearman -0.069, p = 0.28). NB (ML alpha 1.28) Disbiome experiments ~ kscore + log studies + log(1+hits): kscore coef 0.38, p = 0.0017; literature volume coef 0.41, p = 3.6e-13 -> pre-registered E1 PASS.
Verdict: the Disbiome keystone-literature link is not explained by how much a genus is studied; it gets stronger once literature volume is controlled. Still correlational and possibly oral/HACEK-driven.

## Alternative network inference: graphical lasso (pre-registered 3129971; scripts/keystone_gglasso.py, results/keystone_gglasso.json) - H1 FAILED
Keystones re-derived per study from CLR partial-correlation networks (gglasso, lambda1 = 0.1; weighted degree; top 10%), all 160 studies solved.
Process disclosure: the gitignored MGnify tables were re-downloaded; a first fitting pass ran on raw lineage tables before the genus collapse of fetch_mgnify.py was applied. It was caught when the model merge returned no rows, discarded before any result, and all 160 files were re-collapsed with lane B's code (160/160 match the manifest shapes).
- Within-study FE logit top_gl ~ GAI + log abundance + prevalence (9771 rows): GAI coef 0.079, p = 0.15 -> pre-registered H1 FAILS.
- The two methods barely agree on who is a keystone: Cohen's kappa 0.045 on 17499 shared genus-study rows; genus-level keystone fractions rho = 0.012 (p = 0.85, 248 genera).
Verdict: the anaerobe-keystone association is specific to the ridge gLV-form (directed out-strength) keystone definition; it does not appear under an undirected graphical-lasso definition, and the two definitions pick almost unrelated genera. This confirms the standing caveat that keystone status is a property of the inference method. The candidate is downgraded to "method-specific association"; all trait-source and phylogeny replications above test the ridge definition only.

## Wikidata Gram-stain check (pre-registered 0ecdd41, QID fix 1f20b4a; scripts/keystone_wikidata.py, results/keystone_wikidata.json)
Disclosure: the first run used a wrong Gram-positive item id (Q857525 instead of Q857288), giving a constant predictor; it was discarded and the fix committed before the valid run.
3117 Wikidata genera with a single Gram value; 234 keystone-table genera matched; agreement with Madin 95.0% (n = 219; gate passed).
Spearman(frac_top, Gram-negative) = -0.008, p = 0.90 -> the Madin null for Gram stain is replicated. Ridge keystones are not a Gram-negative artefact.

## Sequencing-effort control with ENA (pre-registered 9451f14; scripts/keystone_ena.py, results/keystone_ena.json)
200/203 genera resolved to ENA genus taxIds with public-assembly counts (ENA counts track KEGG genome counts, rho = 0.49).
OLS frac_top ~ GAI + log assemblies + log abundance (HC3, n = 200): GAI slope 0.032, p = 1.8e-09; assemblies slope -0.008, p = 0.26 -> A1 PASS. Keystone fraction is unrelated to sequencing effort (rho = 0.03).
Verdict: the ridge-definition GAI association is not a sequencing-effort artefact. (It remains method-specific; see gglasso.)

## Generalism rival with GBIF (pre-registered 9f6cc62; scripts/keystone_gbif.py, results/keystone_gbif.json)
202/203 genera matched exactly in the GBIF backbone; 196 in the model. OLS frac_top ~ GAI + log occurrences + log countries + log abundance (HC3):
GAI slope 0.019, p = 0.024 -> B1 PASS. Occurrences slope -0.040 (p = 0.0026, negative: keystones are if anything less often recorded); countries p = 0.40. Rival (cosmopolitan generalists) not supported.
Note: GAI effect is smaller here (0.019 vs 0.032 in the ENA model), so part of the signal shares variance with GBIF occurrence volume. Ridge definition only.

## UniProt annotation-pipeline replication (pre-registered c9ea858; scripts/keystone_uniprot.py, results/keystone_uniprot.json)
UGAI = PFOR (EC 1.2.7.1) minus cytochrome-c oxidase (EC 7.1.1.9) entries per recA, reference proteomes only; 198 genera. Validity gate passed: Spearman with KEGG GAI 0.87. (Counts fetched in chunks with the script's own query function after a single run hit the time limit.)
frac_top vs UGAI: rho = 0.29 (p = 3.5e-05); OLS with log abundance: slope 0.022, HC3 p = 0.0013 -> U1 PASS.
Verdict: the ridge-definition anaerobe association replicates with a different annotation pipeline (UniRule/ARBA EC calls); genome sets overlap with KEGG, so it is not a new-genome replication.

## Crossref literature-volume control (pre-registered 6ff904c; scripts/keystone_crossref.py, results/keystone_crossref.json)
Replaces the OpenAlex design (pre-registered 93ee1bc, not run: HTTP 429, key required; not counted). Counts for all 248 genera (median 113). Mechanics: counts were fetched in chunks with the script's own query function (2-6 threads, missing calls retried) after a single run hit the time limit; disclosed here.
C1 Disbiome NB with log(1 + Crossref works): kscore coef 0.35, p = 0.0080 -> PASS (Crossref covariate p = 7.9e-05).
C2 BugSigDB NB with the same covariate: kscore coef 0.21, p = 0.047 -> PASS, marginal (near the threshold).
Caveat: query.bibliographic is a fuzzy relevance search, so counts are a noisy literature proxy. Ridge definition only.

## igraph betweenness keystone definition (pre-registered 0962035; scripts/keystone_igraph.py, results/keystone_igraph.json)
Per-study CLR correlation networks (|r| >= 0.3), igraph betweenness, top = >= 90th percentile and > 0. 160/160 studies had edges (G1 pass); 9,697 genus-study rows in the model.
GAI coef 0.063, clustered p = 0.34 -> I1 FAILED. Agreement with ridge labels: kappa 0.022; genus-level Spearman vs ridge frac_top -0.03 (p = 0.64, 248 genera).
Verdict: a second independent network definition fails. The anaerobe-keystone association is specific to the ridge gLV-form out-strength definition. (Cache columns reuse the gglasso names gl_degree/top_gl; here they hold betweenness and its top label.)

## Ensembl Genomes sequencing-effort control (pre-registered be7175d; scripts/keystone_ensembl.py, results/keystone_ensembl.json)
Counts for all 203 GAI genera (Spearman with ENA assemblies 0.65). OLS frac_top ~ GAI + log10(1 + Ensembl genomes) + log abundance (HC3): GAI slope 0.029, p = 2.2e-07 -> S1 PASS; Ensembl genomes slope -0.008, p = 0.22.
Verdict: the ENA result (A1) replicates with a second, curated genome archive. Free-text counts are noisy. Ridge definition only.

## XGBoost out-of-sample test (pre-registered 9cf67ae; scripts/keystone_xgboost.py, results/keystone_xgboost.json)
200 genera; 20 repeats of 5-fold CV. Adding GAI raised out-of-fold R^2 in 20/20 repeats (mean delta 0.27, sign test p = 1.9e-06) -> X1 PASS by the pre-registered criterion.
Important negative: both models have NEGATIVE absolute out-of-fold R^2 (full -0.11, reduced -0.38), i.e. worse than predicting the mean. XGBoost with these settings overfits at n = 200; GAI makes it less wrong but gives no usable out-of-sample prediction of keystone fraction. The linear OLS associations are not a predictive model.

## InterPro anaerobe-index replication (pre-registered b327560; scripts/keystone_interpro.py, results/keystone_interpro.json)
IGAI from InterPro family counts (PFOR IPR011895, COX1 IPR000883, RecA IPR013765); 198 genera with RecA. Validity gate passed: Spearman with KEGG GAI 0.89. Cache filled over five timed runs of the script itself (pre-registered mechanism).
frac_top vs IGAI: rho 0.29 (p = 2.7e-05); OLS with log abundance: slope 0.021, HC3 p = 0.00024 -> P1 PASS.
Verdict: replicates with signature-based annotation; protein sets overlap with UniProt (tool 29), so not independent genomes. Ridge definition only.

## HOMD oral-taxon rival (pre-registered 0aa4eb0, parser addendum 5658ee6; scripts/keystone_homd.py, results/keystone_homd.json)
46 of 203 GAI genera are oral in HOMD v4.2 (Body Site contains "oral"). OLS frac_top ~ GAI + oral + log abundance (HC3): GAI slope 0.024, p = 3.7e-06 -> M1 PASS. Oral genera do have higher keystone fraction (coef 0.042, p = 0.0084), and 6 of the top 10 ridge keystones are oral. Among the 157 non-oral genera alone, GAI slope 0.024, p = 4.7e-06.
Verdict: oral origin is a real, separate correlate of ridge keystone status but does not explain the GAI association. Ridge definition only.

## RNAcentral rRNA sequencing-effort control (pre-registered 9814c7a; scripts/keystone_rnacentral.py, results/keystone_rnacentral.json)
rRNA sequence counts for all 203 GAI genera (Spearman with ENA assemblies 0.61). OLS frac_top ~ GAI + log10(1 + rRNA) + log abundance (HC3): GAI slope 0.027, p = 8.2e-06 -> R1 PASS; rRNA slope -0.010, p = 0.20.
Verdict: marker-gene sequencing effort does not explain the association. Free-text counts are noisy. Ridge definition only.

## Change of direction: method-general keystone correlate (pre-registered 2934c54; scripts/keystone_methodgeneral.py, results/keystone_methodgeneral.json)
After the gglasso and igraph negatives, we tested whether oral origin (HOMD v4.2) predicts keystone status under all network definitions. Within-study logit top ~ oral + GAI + log abundance + prevalence + C(study), clustered SE.
gglasso: oral coef 0.21, p = 0.027; igraph betweenness: oral coef 0.32, p = 0.0011 -> MG1 PASS (both new tests). GAI stays null under both (p = 0.35, 0.70).
Ridge arm (reported only; the oral effect was seen there before registration): oral coef 0.14, p = 0.17; GAI 0.30, p = 5.7e-06. Note: the ridge logit hit the iteration limit without converging (statsmodels ConvergenceWarning); its numbers are indicative only. The gglasso and igraph fits converged.
Verdict: oral-origin genera are more often network hubs under two independent network definitions, a candidate method-general correlate. It is modest, covariate-adjusted, and not causal. The anaerobe (GAI) association remains ridge-specific.

## Bayesian re-fit of the oral-hub effect (bambi/PyMC; pre-registered 45e3254; results/keystone_bambi.json)
Random study intercepts, 2 chains x 500 draws. gglasso: oral posterior mean 0.25, 95% HDI [0.12, 0.40], P(>0) = 1.00; igraph: 0.33 [0.18, 0.48], P(>0) = 1.00 -> BY1 PASS. Fixed-effect R-hat <= 1.01 (bambi warned R-hat > 1.01 for some other parameter; only 2 chains). GAI HDIs include 0 under both.
Verdict: the HOMD oral effect is not an artefact of the clustered-SE frequentist model.

## Literature oral index replication (NCBI PubTator3; pre-registered 45e3254, mechanics addendum 3d16589; results/keystone_pubtator.json)
Oral literature fraction OLF = articles with "<genus> AND (oral OR dental)" / articles with "<genus>", 203 genera; Spearman with HOMD oral 0.54.
gglasso: OLF_z coef 0.033, p = 0.57; igraph: 0.082, p = 0.23 -> PT1 FAILED. Ridge arm (reported only, fit did not converge): 0.21, p = 0.00015.
Verdict: the method-general oral effect does NOT replicate with a continuous literature-derived oral index; it depends on the curated HOMD oral list. The oral-hub candidate is weakened to "HOMD-list-specific, one of two oral definitions". Next direction: test whether the HOMD effect comes from specific oral-dominant clades (leave-one-family-out).
