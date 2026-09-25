"""Build the item-4 paper (docx) from committed result files. Run from repo root."""
import json, sys
sys.path.insert(0, "paper")
from paperkit import Paper

H = json.load(open("results/mdsine2_headtohead_healthy.json"))
U = json.load(open("results/mdsine2_headtohead_uc.json"))
B = {d: json.load(open(f"results/bench_{d}_presence_mean_cnode_glv_graphtwin_k10.json"))
     for d in ["Drosophila_Gut", "Soil_Vitro", "Human_Oral", "Human_Gut"]}

P = Paper("Population Priors Rival Interaction Models in Microbiome Digital Twins: "
          "a Leave-One-Out Audit of cNODE and a Head-to-Head with MDSINE2",
          "MEGA-PROGRAM-27, Item 4 - Udita Phookan (program owner); computational work by an AI research agent. Revised draft of 25 September 2026.")

P.h("Abstract")
P.p("A microbiome digital twin is a model that, given what we know about a community, predicts what it will look like: its steady-state "
    "composition after assembly, or its trajectory under perturbation. Two published approaches are compositional neural ODEs "
    "(cNODE; Michel-Mata et al., 2022) for assemblage-to-composition prediction, and MDSINE2 (Gibson et al., Nature Microbiology 2025) "
    "for forecasting absolute abundances in gnotobiotic mice through diet and antibiotic perturbations. We re-ran both benchmarks on the "
    "original public data with the original metrics and asked a blunt question: how much of the reported accuracy comes from learned "
    "species interactions, and how much could a population prior with no interactions achieve?")
P.p("Findings. (1) On the six cNODE ecosystems under leave-one-out, a parameter-free presence-only null (mean training composition "
    "restricted to present taxa) is clearly beaten by cNODE on ocean, soil and Drosophila data, but on both human-associated datasets the "
    "published cNODE median Bray-Curtis error (oral 0.211, gut 0.242) falls inside the 95% bootstrap interval of the null "
    "(0.204 [0.188, 0.222] and 0.259 [0.236, 0.271]). (2) On the MDSINE2 ulcerative-colitis cohort, a presence-conditional population "
    f"forecaster that uses no species interactions reaches a median RMSE of {U['PresenceConditionalPopulation (ours)']['median']:.3f} "
    "(log10 abundance, official metric), the lowest of the 12 methods in the paper's source data; it beats MDSINE2 without modules "
    f"(0.805; Wilcoxon p = {U['MDSINE2 (No Modules)']['wilcoxon_p']:.1e}) and full MDSINE2 (1.093; p = {U['MDSINE2']['wilcoxon_p']:.1e}) "
    f"on the same {U['MDSINE2']['n']} subject-taxon pairs. (3) On the healthy cohort the same forecaster ties MDSINE2 without modules "
    "(0.919 vs 0.913, p = 0.53), beats full MDSINE2 (1.061, p = 1.1e-4), and is beaten by RA-MDSINE2 without modules (0.883, p = 0.045).")
P.p("(4) Under a stricter metric that scores every timepoint, the same forecaster ranks first on both MDSINE2 cohorts (UC 1.654 vs "
    "MDSINE2 without modules 1.824; healthy 1.752 vs 2.072; p < 1e-39), which falsified our own prediction that the advantage came from the "
    "detection-only metric. (5) At scale the picture changes: across 160 MGnify studies in 8 biomes, an interaction model beats a calibrated "
    "presence prior in 121 studies (FDR < 0.05), so the human-data null of finding (1) does not generalise. We ship the microtwin command-line "
    "tool (audit and forecast) so anyone can run this audit on their own abundance table.")
P.p("(6) Exploratory keystone analysis names one candidate, the anaerobe-keystone hypothesis: across 156 studies, genera made of strict anaerobes are "
    "more often network hubs within the same study (study fixed-effect logit, p = 1.4e-4), independent of abundance and prevalence, and sulfate "
    "reducers are enriched under both NCBI and GTDB taxonomies (q = 0.02); a KEGG genomic anaerobe index replicates it (p = 7e-8). No single biome passes FDR and keystones come from inferred networks, "
    "but the association fails with graphical lasso and igraph betweenness keystone definitions. It is a ridge-specific candidate, not a cross-method ecological discovery. A distinct HOMD oral-list effect survives those two methods but fails a PubTator literature-index replication.")
P.p("Caveats. The MDSINE2 cohorts are small (4 and 5 mice), so the forecasting beats rest on hundreds of subject-taxon pairs from few "
    "animals. Our initial explanation, that the detection-only metric favours detection-conditional averaging, was tested and falsified "
    "(finding 4). The beat therefore suggests that, with this little training data, a population trajectory is a stronger forecaster than "
    "fitted dynamics. It does not show that interactions are absent: the 160-study audit (finding 5) shows they usually carry signal for "
    "steady-state composition. Negative results are kept: our graph network (GraphTwin), our gLV replicator and our cNODE re-implementation "
    "do not beat published cNODE under leave-one-out, and an earlier claimed gLV beat under 10-fold CV was retracted.")

P.h("1. Introduction")
P.p("Digital twins of the microbiome promise in-silico trials: remove a species, add an antibiotic, change a diet, and read out the "
    "community before touching an animal or a patient. The community therefore invests heavily in interaction-aware models: generalised "
    "Lotka-Volterra (gLV) systems, Bayesian gLV with interaction modules (MDSINE, MDSINE2), and neural ODEs (cNODE). Their value rests on a "
    "premise that is rarely tested directly: that the interaction terms carry predictive information beyond what a population average "
    "already provides.")
P.p("Strong baselines matter because microbiome data are dominated by taxon identity. A taxon that is abundant in one host is usually "
    "abundant in another. A predictor that simply remembers typical abundances, conditioned on which taxa are present, may already explain "
    "most of the variance. If so, the headline accuracy of an interaction model says little about whether its interactions are right, and "
    "downstream uses such as keystone-species ranking or perturbation design rest on weaker ground than the accuracy suggests.")
P.p("We test that premise on the two public benchmarks that serve as reference benchmarks for two twin tasks. Our contributions are: "
    "(i) an exact leave-one-out re-run of the cNODE benchmark with a bootstrap null interval; (ii) a verified reproduction of the MDSINE2 "
    "cross-validation metric from the authors' notebook and Source Data, matching the published MDSINE2 median; (iii) a presence-conditional "
    "population forecaster that tops the UC leaderboard and ties the healthy one; and (iv) an explicit account of why the metric allows this.")

P.h("2. Problem statements and notation")
P.h("2.1 Assemblage-to-composition (cNODE task)", 2)
P.p("Let N be the species pool. A sample is a binary assemblage z in {0,1}^N and an observed steady-state composition p on the simplex "
    "with supp(p) contained in supp(z). A twin is a map phi: z -> p-hat. Error is Bray-Curtis dissimilarity:")
P.equation("BC(p, q) = sum_i |p_i - q_i| / sum_i (p_i + q_i)")
P.p("cNODE (Michel-Mata et al., 2022) defines phi(z) = x(1), with x solving the replicator-type ODE")
P.equation("dx/dt = x ⊙ ( f(x) - 1 x^T f(x) ),   f(x) = W x,   x(0) = z / |z|")
P.p("so that sum_i x_i is conserved and absent taxa stay at zero. Our presence-only null is")
P.equation("p-hat_i(z) = z_i m_i / sum_j z_j m_j,   m_i = (1/|T|) sum_{s in T} p_{s,i}")
P.p("where T is the training set. It has no interaction parameters; its only parameters are the N training means. Our gLV replicator "
    "baseline integrates")
P.equation("dx/dt = x ⊙ ( r + A x - phi(x) 1 ),   phi(x) = x^T (r + A x)")
P.p("to a fixed horizon, and GraphTwin applies attention message passing over present taxa:")
P.equation("m_i = sum_{j in S, j != i} alpha_ij g_ij V h_j,   alpha_ij = softmax_j( q_i^T k_j / sqrt(d) ),   g_ij = sigma( e_i^T U e_j )")
P.p("followed by a residual update h_i <- LayerNorm(h_i + MLP([h_i, m_i])) and a masked softmax over S = supp(z) added to the log-prior log m_i.")
P.h("2.2 Held-out-subject forecasting (MDSINE2 task)", 2)
P.p("For subject s, taxon i and time t, let x_{s,i}(t) be absolute abundance (relative abundance times total 16S qPCR load). A forecaster "
    "sees the training subjects' full trajectories, the perturbation schedule and the held-out subject's initial state, and predicts "
    "x-hat_{s,i}(t) for all t. The MDSINE2 paper's evaluation (paper_figures/fig3_cross_validation.ipynb) computes, per (subject, taxon),")
P.equation("RMSE_{s,i} = sqrt( (1/|D_{s,i}|) sum_{t in D_{s,i}} ( log10(x_{s,i}(t) + eps) - log10(x-hat_{s,i}(t) + eps) )^2 ),   D_{s,i} = { t : x_{s,i}(t) > 1e-5 }")
P.p("with eps = 1e3 in the notebook's units, and reports the distribution of RMSE_{s,i} over all pairs. Note the set D_{s,i}: only timepoints "
    "with detected truth are scored. Our presence-conditional population forecaster is")
P.equation("mu_i(t) = mean_{o in O : x_{o,i}(t) > 0} log10 x_{o,i}(t),   log10 x-hat_{s,i}(t) = mu_i(t) + w(t) [ log10 x_{s,i}(t0) - mu_i(t0) ]")
P.equation("w(t) = exp( -(t - t0) / tau ),   tau chosen by inner leave-one-subject-out over O")
P.p("with O the training subjects, trajectories linearly interpolated onto the held-out subject's sampling days, and a fallback to the "
    "unconditional mean when no training subject detects the taxon at t. Paired comparisons use the two-sided Wilcoxon signed-rank test "
    "over (s, i) pairs:")
P.equation("W = sum_k sgn(d_k) R_k,   d_k = RMSE^ours_k - RMSE^other_k")
P.p("and bootstrap intervals for the null's median use 5000 resamples of the leave-one-out error vector:")
P.equation("CI_95 = [ Q_0.025, Q_0.975 ] of { median( e*_b ) }_{b=1..5000},   e*_b ~ resample(e)")
P.h("2.3 Why the detection-conditional metric favours population priors", 2)
P.p("Write the loss restricted to detected timepoints as E[(y - y-hat)^2 | detected]. The minimiser over predictors that do not see the "
    "held-out trajectory is the conditional mean E[y | detected, t, i], which is exactly what mu_i(t) estimates from the training subjects. "
    "A dynamical model trained on all timepoints, or simulating extinctions, may predict low abundance where the truth happens to be "
    "detected, and pays heavily for it; its errors where the truth is undetected are never scored. This is a structural bias of the "
    "metric in favour of detection-conditional averaging, which we state as:")
P.equation("argmin_{f} E[ (Y - f(i,t))^2 | Y > L ] = E[ Y | Y > L, i, t ]  (for predictors f independent of the held-out trajectory)")

P.h("3. Data")
P.p("All data are public, unmodified, and fetched by accession. Table 1 is the dataset manifest. We count 169 distinct primary accession-level datasets: the nine below plus 160 MGnify studies (Appendix A). The datasets ledger also records secondary trait and literature reference tables; these are not independent cohorts.")
P.table(["#", "dataset", "source / accession", "n", "use"], [
    [1, "Ocean", "github.com/yixueyang/cNODE (Michel-Mata 2022)", 269, "cNODE benchmark"],
    [2, "Drosophila gut", "same", B["Drosophila_Gut"]["n"], "cNODE benchmark"],
    [3, "Soil in vitro", "same", B["Soil_Vitro"]["n"], "cNODE benchmark"],
    [4, "Soil in vivo", "same", 678, "cNODE benchmark"],
    [5, "Human oral", "same", B["Human_Oral"]["n"], "cNODE benchmark (de-dup: 143 vs 150 reported)"],
    [6, "Human gut", "same", B["Human_Gut"]["n"], "cNODE benchmark"],
    [7, "MDSINE2 healthy cohort (counts, qPCR, perturbations)", "github.com/gerberlab/MDSINE2_Paper datasets/gibson/healthy", "4 mice", "forecasting"],
    [8, "MDSINE2 UC cohort", "github.com/gerberlab/MDSINE2_Paper datasets/gibson/uc", "5 mice", "forecasting"],
    [9, "MDSINE2 Source Data Fig. 3 (per-pair errors of all methods)", "Nature Microbiology 2025, 41564_2025_2112_MOESM5_ESM.xlsx", "556 / 601 pairs", "head-to-head"],
], "Dataset manifest (distinct, accession-level). n = samples or subjects.")
P.p("The cNODE datasets hold assemblage-composition pairs from ocean plankton, Drosophila gut communities, soil communities in vitro and "
    "in vivo, and human oral and gut 16S surveys. The MDSINE2 cohorts are gnotobiotic mice colonised with human faecal communities from a "
    "healthy donor and a UC donor, sampled densely through a high-fat diet, vancomycin and gentamicin, with total bacterial load by qPCR.")

P.h("4. Methods")
P.h("4.1 cNODE audit", 2)
P.p("We followed the leave-one-out protocol of the cNODE paper: each sample is held out once, the model is fit on the rest, and the "
    "median Bray-Curtis error over held-out samples is reported. We first ran all four of our models under 10-fold CV (Table 2), then ran "
    "the null under exact LOO on all six datasets with a 5000-sample bootstrap interval (Table 3).")
P.h("4.2 MDSINE2 reproduction", 2)
P.p("We re-implemented the metric from the authors' notebook and applied it to the per-pair predictions in their Source Data. Our "
    "recomputed MDSINE2 median on the healthy cohort is 1.061, matching the published box plot, which verifies the pipeline. Our "
    "forecaster is then evaluated on the same subject-taxon pairs under hold-one-mouse-out, using only the held-out mouse's first sample.")
P.h("4.3 Software and hermetic tests", 2)
P.p("The code is in src/microtwin (data.py, models.py, evaluate.py, dynamics.py, popforecast.py). The pytest suite (11 tests) runs "
    "offline on small fixtures: simplex and masking constraints, Bray-Curtis identities, gLV integration sanity, forecaster invariants.")

P.h("5. Results")
P.h("5.1 cNODE benchmark: interactions help outside humans, not detectably on human data", 2)
rows = []
for d, b in B.items():
    m = b["median"]
    rows.append([d.replace("_", " "), b["n"], b["taxa"], m["presence_mean"], m["cnode"], m["glv"], m["graphtwin"], b["published_cnode_median"]])
P.table(["dataset", "n", "taxa", "null", "cNODE (ours)", "gLV (ours)", "GraphTwin (ours)", "cNODE published"], rows,
        "10-fold CV median Bray-Curtis on four cNODE datasets. Published cNODE uses LOO, so this table is indicative only.")
P.table(["dataset", "n", "null LOO median", "95% CI", "published cNODE", "cNODE inside null CI?"], [
    ["Ocean", 269, 0.094, "[0.089, 0.101]", 0.060, "no - cNODE better"],
    ["Drosophila gut", 24, 0.170, "[0.100, 0.193]", 0.066, "no - cNODE better"],
    ["Soil in vitro", 48, 0.198, "[0.085, 0.268]", 0.079, "no - cNODE better"],
    ["Soil in vivo", 678, 0.124, "[0.119, 0.127]", 0.107, "no - cNODE better"],
    ["Human oral", 143, 0.204, "[0.188, 0.222]", 0.211, "YES"],
    ["Human gut", 106, 0.259, "[0.236, 0.271]", 0.242, "YES"],
], "Exact leave-one-out null vs published cNODE.")
P.figure("results/figures/fig_null_vs_cnode.png", "Presence-only null (LOO median with 95% bootstrap CI) against published cNODE on the six ecosystems.")
P.p("Interpretation. On non-human systems cNODE's interactions buy a large, clear gain. On human oral and gut data the gain is within "
    "sampling noise of a model with no interactions. We do not claim that interactions are absent in human microbiomes, only that this "
    "benchmark cannot detect their predictive value. Our GraphTwin, a larger model, does no better (human gut 0.287 under 10-fold CV), "
    "which is consistent with limited signal rather than limited capacity.")
P.h("5.2 MDSINE2 benchmark: UC beat, healthy tie", 2)
def tab(D):
    r = []
    for k, v in sorted(D.items(), key=lambda kv: kv[1]["median"]):
        r.append([k, round(v["median"], 3), round(v["mean"], 3), v["n"], v.get("ours_better_pairs", "-"),
                  round(v["mean_diff_ours_minus"], 3) if "mean_diff_ours_minus" in v else "-",
                  ("%.1e" % v["wilcoxon_p"]) if "wilcoxon_p" in v else "-"])
    return r
P.table(["method", "median", "mean", "pairs", "ours better", "mean diff (ours-other)", "Wilcoxon p (2-sided)"], tab(U), "UC cohort, official MDSINE2 metric, hold-one-mouse-out.")
P.table(["method", "median", "mean", "pairs", "ours better", "mean diff (ours-other)", "Wilcoxon p (2-sided)"], tab(H), "Healthy cohort, same protocol.")
P.figure("results/figures/fig_mdsine2_headtohead.png", "Median per-(mouse, taxon) RMSE of log10 absolute abundance on detected timepoints. Red: our presence-conditional population forecaster.", 6.5)
P.p("On UC the forecaster ranks first of 12 and is better than MDSINE2 without modules in 376 of 601 pairs. On healthy it ranks third "
    "of 11. Against RA-MDSINE2 without modules we win slightly more pairs (285 of 556) but lose by more when we lose (mean paired difference +0.095 in their favour); the signed-rank test favours them (two-sided p = 0.045). Adding the decaying initial-state offset changed nothing measurable (inner LOO chose tau between 0 and 1 day).")

import pandas as _pd
MG = json.load(open("results/mgnify_audit_summary.json")); MA = _pd.read_csv("results/mgnify_audit_fdr.csv"); MM = _pd.read_csv("data/raw/mgnify/manifest.csv")
P.h("5.3 Scale-up: interaction audit across 160 MGnify studies", 2)
P.p(f"To test whether the human-data null generalises, we fetched study-level SSU genus tables for {MG['studies']} MGnify studies "
    "(8 biomes, at least 20 samples each; accessions in Appendix A) and asked, per study, whether an interaction model beats a calibrated "
    "presence prior at predicting composition from the assemblage. The prior is the two-way log-linear fit")
P.equation("log p_si = mu_i + c_s  (present entries only),   p-hat_i(z) = z_i e^(mu_i) / sum_j z_j e^(mu_j)")
P.p("in which the sample offset c_s absorbs the closure constant, so mu is not biased by which other taxa are present. The interaction "
    "model adds a steady-state generalised Lotka-Volterra shift fitted by ridge regression:")
P.equation("p-hat_i(z) ∝ z_i exp( mu_i + b_i + sum_j W_ij z_j ),   (b_i, W_i) = argmin sum_{s: z_si=1} (log p_si - mu_i - c_s - b_i - W_i z_s)^2 + lambda ||W_i||^2")
P.p("with lambda chosen by inner 3-fold CV. We used 5-fold outer CV, median Bray-Curtis error, a paired Wilcoxon test per study, and "
    "Benjamini-Hochberg FDR across studies:")
P.equation("q_(k) = min_{j >= k} ( m p_(j) / j )")
P.p(f"Interactions were better at FDR < 0.05 in {MG['interaction_better_fdr05']} of {MG['studies']} studies, the prior in "
    f"{MG['prior_better_fdr05']}, and neither in {MG['no_difference']}; median relative gain {100*MG['median_relative_gain']:.1f}%.")
P.table(["biome", "studies", "interactions better", "prior better", "median gain (BC)", "median prior BC"],
        [[r["biome_short"], r["studies"], r["int_wins"], r["prior_wins"], round(r["median_gain"], 3), round(r["median_prior_bc"], 3)] for r in MG["per_biome"]],
        "Interaction audit by biome (results/mgnify_audit_summary.json).")
P.figure("results/figures/fig_mgnify_audit.png", "Relative gain of the interaction model per study. Red: interactions better (FDR < 0.05); dark: prior better; grey: no difference.", 6.5)
P.p("A candidate exception, the human digestive system (21 of 41), did not survive scrutiny: 33 of the 41 gut studies are metagenome "
    "assemblies, against 2 of 118 other studies, and the 8 amplicon gut studies show the same relative gain as other biomes (0.210 vs 0.184). "
    "Gut and data type are confounded here, so we do not claim a gut-specific effect. This larger audit also means the cNODE null result "
    "(Section 5.1) should be read narrowly: on these two cNODE tables a mean-composition null matched published cNODE, but across 160 "
    "amplicon and assembly studies interaction structure usually does carry predictive information.")

KC = _pd.read_csv("results/keystone_consensus.csv"); PR = json.load(open("results/predictors_audit.json"))
P.h("5.4 Keystone consensus across studies (exploratory)", 2)
P.p("For each MGnify study we fitted the ridge interaction model on all samples, built a directed networkx graph with edge weight |W_ij|, "
    "and scored each genus by weighted out-strength. A genus is 'top' in a study if it is in that study's top 10%. Across studies we test "
    "the top count against the 10% expectation with a one-sided binomial test and control the false discovery rate (Benjamini-Hochberg):")
P.equation("s_j = sum_i |W_ij|,   p_j = P(Binom(n_j, 0.1) >= k_j),   q_(r) = min_{r' >= r} ( m p_(r') / r' )")
P.table(["genus", "studies", "top", "fraction top", "p", "q (BH)"],
        [[r.genus, int(r.studies), int(r.top), round(r.frac_top, 3), f"{r.p:.1e}", f"{r.q_bh:.2g}"] for r in KC.head(7).itertuples()],
        f"Top genera by keystone consensus ({len(KC)} genera modelled in >= 20 studies; results/keystone_consensus.csv).")
P.p("Two genera pass FDR < 0.05: Cardiobacterium and Eikenella. Both are oral HACEK genera, so the signal most likely reflects the oral studies, "
    "where interaction models fit best. It is not a cross-biome keystone law. Out-strength from a ridge model is a statistical dependence score, "
    "not a causal keystone effect, and it scales with each genus's variance and prevalence. No experimental validation was done.")

KP = _pd.read_csv("results/keystone_phylum_enrichment.csv"); KB = json.load(open("results/keystone_bugsigdb.json"))
P.p("Phylogeny. Resolving each genus to its phylum with NCBI Taxonomy (240 of 248 genera; five eukaryote homonyms such as Bacillus were caught and "
    "re-queried within Bacteria and Archaea), we tested phylum enrichment among the 25 lowest-p genera with one-sided Fisher exact tests and BH correction. "
    f"Only {KP.iloc[0].phylum} (sulfate reducers) is enriched: {int(KP.iloc[0].top25)} of {int(KP.iloc[0]['all'])} genera (Desulfobulbus, Desulfovibrio, Bilophila), "
    f"p = {KP.iloc[0].p:.3f}, q = {KP.iloc[0].q_bh:.3f}. With three genera, this is a hypothesis (hydrogen and sulfur cross-feeding hubs), not a result.")
P.p(f"Literature cross-check. Across {KB['n_signatures_in_bugsigdb']:,} published genus-level differential-abundance signatures in BugSigDB, a negative-binomial "
    "model of signature counts on keystone score, adjusting for how many studies a genus appears in, gives a positive coefficient that is not robust: "
    f"p = {KB['nb_p_kscore']:.3f} with dispersion fixed at 1 and p = {KB['nb_ml_p_kscore']:.3f} with dispersion estimated (alpha = {KB['nb_ml_alpha']:.2f}). "
    "Keystone-consensus genera are not clearly over-represented in the disease literature.")
P.equation("log E[n_j] = c_0 + c_1 (-log10 p_j) + c_2 log(studies_j),   Var(n_j) = mu_j + alpha mu_j^2")

KG = json.load(open("results/keystone_gtdb.json"))
P.p(f"GTDB replication. Re-mapping the genera to the Genome Taxonomy Database (release v232, bac120; {KG['n_mapped']} of {KG['n_total']} genera) gives the same result: "
    f"Desulfobacterota {KG['gtdb_phylum'][0]['top25']} of {KG['gtdb_phylum'][0]['all']}, p = {KG['gtdb_phylum'][0]['p']:.4f}, q = {KG['gtdb_phylum'][0]['q_bh']:.3f}. "
    f"NCBI and GTDB disagree on the phylum of only {len(KG['ncbi_vs_gtdb_phylum_disagreements'])} genera, mostly renamings. No family passes FDR "
    f"(best: {KG['gtdb_family'][0]['taxon']} and {KG['gtdb_family'][1]['taxon']}, q = {KG['gtdb_family'][0]['q_bh']:.2f}). The result does not depend on the taxonomy, but it still rests on three genera.")

P.h("5.4.1 Physiological traits of keystones: the anaerobe-keystone candidate", 3)
KT = _pd.read_csv("results/keystone_traits_tests.csv"); KCF = json.load(open("results/keystone_traits_confound.json"))
KBI = json.load(open("results/keystone_traits_biome.json")); KAB = json.load(open("results/keystone_traits_abundance.json"))
P.p("We joined each genus to the Madin et al. (2020) trait database (14,893 species; condensed_species_NCBI.csv), aggregating species to genus as the share of "
    "strict anaerobes, Gram-negative, motile and sporulating species, and the median genome size, GC content and doubling time. We test each trait against "
    "keystone frequency (Spearman, BH across traits) and top-25 membership (Mann-Whitney).")
P.table(["trait", "genera", "Spearman rho", "q (BH)", "top-25 mean", "rest mean", "Mann-Whitney q"],
        [[r.trait, int(r.n), round(r.spearman_rho, 3), f"{r.q_spearman:.2g}", f"{r.top25_mean:.3g}", f"{r.rest_mean:.3g}", f"{r.q_mw:.2g}"] for r in KT.itertuples()],
        "Keystone frequency vs genus traits (results/keystone_traits_tests.csv).")
P.p(f"Strict-anaerobe share and small genome size track keystone frequency; the other traits do not. The anaerobe effect keeps its sign and significance in a "
    f"rank regression with genome size and log study count (p = {KCF['ols_pvalues']['r_anaerobe']:.1e}, HC3) and under permutation within study-count quintiles "
    f"(p = {KCF['strat_perm_p']:.1e}). Because biome could confound this (anaerobes dominate gut studies), we ran two falsification tests inside studies. "
    f"First, within each of {KBI['within_study']['n_studies']} studies we compared keystones with the other genera: keystones have the higher anaerobe share in "
    f"{KBI['within_study']['frac_positive']*100:.0f}% of studies (mean difference {KBI['within_study']['mean_diff']:+.3f}, sign-flip p = {KBI['within_study']['signflip_p']:.1e}). "
    "Second, we fitted a logistic model with study fixed effects and study-clustered standard errors, adding abundance and prevalence:")
P.equation("logit P(top_js = 1) = a_s + b_1 anaerobe_j + b_2 log10(mean RA_js) + b_3 prevalence_js")
P.p(f"On {KAB['n_rows']:,} genus-study rows from {KAB['n_studies']} studies, b_1 = {KAB['full']['coef']['anaerobe']:.2f} (p = {KAB['full']['p']['anaerobe']:.1e}), almost the same as "
    f"without abundance terms ({KAB['no_abund']['coef']['anaerobe']:.2f}). Anaerobe share is nearly uncorrelated with abundance (r = {KAB['corr_anaerobe_lra']:.2f}). "
    "So the association is not a biome mix or abundance artifact.")
bb = {k.split(':', 1)[1]: v for k, v in KBI["within_study"].items() if k.startswith("biome:")}
KK = json.load(open("results/keystone_kegg.json"))
P.p(f"Genomic replication (KEGG). To avoid relying on one phenotype database, we scored marker genes across {KK['n_kegg_genomes']:,} KEGG genomes "
    f"({KK['n_genera_mapped']} of {KK['n_genera']} genera mapped): pyruvate:ferredoxin oxidoreductase (PFOR; K00169 or K03737), [FeFe]-hydrogenase, "
    "complete dissimilatory sulfate reduction (dsrA, dsrB and aprA), aa3 cytochrome c oxidase (coxA, K02274), catalase and cytochrome bd. The genomic anaerobe index is")
P.equation("GAI_j = (1/|g_j|) sum_{x in g_j} 1[PFOR in x]  -  (1/|g_j|) sum_{x in g_j} 1[coxA in x]")
P.p(f"It agrees with the Madin anaerobe share (Spearman {KK['vs_madin_anaerobe']['GAI'][0]:.2f}) and tracks keystone frequency (rho = {KK['vs_frac_top']['GAI'][0]:.2f}, "
    f"p = {KK['vs_frac_top']['GAI'][1]:.0e}). In the within-study fixed-effect logit with abundance and prevalence ({KK['fe_logit_GAI']['n_rows']:,} rows, "
    f"{KK['fe_logit_GAI']['n_studies']} studies), GAI has coefficient {KK['fe_logit_GAI']['coef']['GAI']:.2f} (p = {KK['fe_logit_GAI']['p']['GAI']:.0e}). "
    f"Most of this is the absence of aerobic respiration (coxA {KK['fe_logit_PFOR_coxA']['coef']['coxA']:.2f}, p = {KK['fe_logit_PFOR_coxA']['p']['coxA']:.0e}; "
    f"PFOR alone p = {KK['fe_logit_PFOR_coxA']['p']['PFOR']:.2f}), plus complete sulfate reduction ({KK['fe_logit_DSR']['coef']['DSR']:+.2f}, p = {KK['fe_logit_DSR']['p']['DSR']:.0e}).")
KBV = json.load(open("results/keystone_bvbrc.json"))
P.p(f"Third source (BV-BRC). Oxygen-requirement annotations of {KBV['n_bvbrc_genomes_annotated']:,} BV-BRC genomes cover {KBV['n_genera_bvbrc']} keystone genera "
    f"(>= 3 annotated genomes). Their anaerobe share agrees with Madin (rho = {KBV['rho_vs_madin'][0]:.2f}) and KEGG GAI (rho = {KBV['rho_vs_kegg_gai'][0]:.2f}), "
    f"tracks keystone frequency (rho = {KBV['rho_vs_frac_top'][0]:.2f}, p = {KBV['rho_vs_frac_top'][1]:.0e}), and keeps its effect in the fixed-effect logit "
    f"(coefficient {KBV['fe_logit']['coef']['bv_anaerobe']:.2f}, p = {KBV['fe_logit']['p']['bv_anaerobe']:.0e}; {KBV['fe_logit']['n_rows']:,} rows, {KBV['fe_logit']['n_studies']} studies). "
    "The three trait sources overlap partly in their curated inputs, so they are not fully independent.")
P.table(["biome", "studies", "mean difference (top - rest)", "p (sign-flip)", "q (BH)"],
        [[b, v["n"], f"{v['mean_diff']:+.3f}", f"{v['p']:.3f}", f"{v['q_bh']:.2f}"] for b, v in bb.items()],
        "Within-study anaerobe difference by biome (results/keystone_traits_biome.json).")
P.p("It is positive in 7 of 8 biomes but no single biome passes FDR (smallest q = 0.10). We name it the anaerobe-keystone hypothesis: genera made of strict "
    "anaerobes rank as network hubs more often, independent of biome, abundance and prevalence. It is falsified if (a) it fails in an independent cohort with "
    "a single biome and adequate power, or (b) perturbation experiments show inferred out-strength does not predict community response. Keystone status here comes "
    "from our own inferred networks; the gglasso and igraph tests below fail. It is a method-specific candidate property of ridge interaction inference, not a proven ecological law.")

P.h("5.4.2 Stress tests and change of direction", 3)
P.p("All checks in this section were pre-registered in commits before analysis and are reproducible from the corresponding scripts and JSON outputs. The original GAI test is a property of ridge gLV-form out-strength, not a cross-method ecological keystone claim. Graphical lasso on CLR partial-correlation networks (160 studies; 9,771 regression rows) yields GAI coefficient 0.079, p=0.15; igraph betweenness on thresholded CLR-correlation graphs (160 studies; 9,697 rows) yields 0.063, p=0.34. Agreement with ridge keystone labels is low (Cohen kappa 0.045 and 0.022 respectively). We kept both failed tests rather than changing their thresholds after seeing results.")
P.equation("logit P(top_js^method = 1) = alpha_s + beta_G GAI_j + beta_O oral_j + beta_A log10(RA_js+10^-6) + beta_P prevalence_js")
P.p("Independent checks of the ridge-only GAI effect address distinct rivals, not the network-definition failure. Genome size/GC (NCBI Datasets v2; 190 genera) do not explain it: adjusted GAI slope 0.028, HC3 p=1.3e-6, versus genome-size p=0.33. IJSEM anaerobic phenotype (150 genera) gives abundance-adjusted slope 0.059, p=6.7e-7, but IJSEM is a source within the Madin compilation and is not independent. Phylogenetic GLS on the GTDB tree gives GAI slope 0.037 at ML lambda (p=4.3e-7) and 0.032 under Brownian covariance (p=0.0064); an Open Tree synthetic topology gives 0.028, Brownian p=0.017. Synthetic-tree branch lengths are artificial. ProTraits coverage of 51 genera misses its 100-genus gate; its non-significant subset is retained as uninformative, not a replication. For every test in this paragraph, the ridge endpoint remains the same.")
P.p("Additional annotation and sampling controls: ENA assemblies (200 genera) leave GAI p=1.8e-9; Ensembl Genomes (203) p=2.2e-7; RNAcentral rRNA sequence counts (203) p=8.2e-6. The assembly or rRNA count terms themselves were null. UniProt EC calls (198) yield a related index with abundance-adjusted p=0.0013; InterPro signatures (198) yield p=0.00024, but their protein sets overlap. A GBIF occurrence/country adjustment reduces the GAI slope to 0.019 (p=0.024), indicating shared variance with a noisy generalism proxy. Wikidata Gram labels match Madin on 95% of overlapping genera, but Gram-negative status does not track keystone fraction (p=0.90). None of these controls removes the network-method caveat.")
P.p("The disease-literature association was checked in Disbiome and BugSigDB. Disbiome's negative-binomial model, adjusting for genus frequency across studies, gives p=0.024; controlling the number of Europe PMC articles gives p=0.0017. Crossref works count gives Disbiome p=0.0080 and BugSigDB p=0.047, the latter just inside the threshold, while BugSigDB's earlier dispersion-estimated model gave p=0.062. These are associations between two published-data proxies; oral HACEK genera and fuzzy name queries remain confounds.")
P.p("After the network-method negatives, we changed direction within the same project. HOMD v4.2 classifies 46 of 203 GAI genera as oral. The ridge genus-level GAI slope remains 0.024 (p=3.7e-6) after adjustment for oral status; HOMD oral coefficient is 0.042 (p=0.0084). On new method-general tests using study-fixed-effect logits with abundance, prevalence and GAI, oral origin has positive coefficients under graphical lasso (0.211; p=0.0265) and igraph (0.322; p=0.00105). GAI is null in those methods. A Bayesian random-study-intercept re-fit gives P(oral coefficient>0)=1.0 for both with two chains of 500 draws; this is a model check, not an independent cohort. Leaving out each of five multi-genus HOMD families keeps the oral association significant in ten fits (gglasso p=0.0197-0.0433; igraph p=0.0003-0.0028).")
P.p("A separate, pre-registered PubTator3 oral/dental literature fraction did not replicate the binary HOMD effect: despite 203 measured genera, graphical-lasso p=0.57 and igraph p=0.23. The index correlates with HOMD membership (rho=0.54) but is a different, literature-biased construct. Bio.Phylo gives no oral clustering on the Open Tree topology (p=0.53). Thus the defensible claim is a HOMD-list-specific candidate for network hubs under two definitions, not an oral-genus law or causality. The ridge oral coefficient in the per-study model is nonsignificant (p=0.17) and its fit did not converge; we do not claim a three-method result.")
P.h("5.4.3 Predictive and software checks", 3)
P.p("On the ridge-only genus-level keystone fraction, XGBoost with 20 repeats of five-fold cross-validation gains mean out-of-fold R2 of 0.27 from GAI (20/20 positive deltas) but has negative absolute R2 (-0.11 with GAI, -0.38 without). That model is not usable for prediction. Separately pre-registered shallower boosters on 200 genera produce mean full-data out-of-fold R2 0.133 for LightGBM (reduced -0.071) and 0.119 for CatBoost (reduced -0.045), both with 20/20 positive deltas. The modest improvement is within the same dataset and outcome. SHAP TreeExplainer ranks GAI first in the fitted LightGBM model (mean absolute contribution 0.0265 versus ENA 0.00772 and abundance 0.00576), an in-sample explanation rather than proof of causality. SymPy verifies the cNODE and gLV vector fields are tangent to the simplex and zero on absent-taxon boundaries for a generic three-taxon system when abundances sum to one. That algebra does not prove numerical stability or predictive accuracy.")
P.table(["analysis", "scope", "pre-registered verdict", "key caveat"], [
    ["gglasso / igraph GAI", "160 MGnify studies", "FAIL / FAIL", "ridge-specific effect"],
    ["HOMD oral on gglasso / igraph", "46 of 203 GAI genera oral", "PASS / PASS", "PubTator index failed"],
    ["HOMD family deletions", "5 families; 10 fits", "PASS", "same curated list"],
    ["LightGBM / CatBoost", "200 genera; repeated CV", "PASS / PASS", "modest, ridge-only R2"],
    ["Bio.Phylo oral topology", "160 tips; 38 oral", "FAIL", "synthetic topology"],
], "Key post-audit tests. Primary methods, thresholds, preregistrations and full negative results are in results/finding_keystone.md and the JSON files.")

P.h("5.5 What predicts where interactions help?", 2)
P.p("Across the 160 studies we regressed the audit gain (prior error minus interaction error) on standardised study covariates: Shannon "
    "diversity and Bray-Curtis dispersion (scikit-bio), co-occurrence network density and modularity (networkx; edges where |Spearman rho| > 0.3 "
    "among genera with prevalence >= 20%), log sample and taxa counts, and assembly and human-gut flags. Inference uses heteroskedasticity-robust (HC3) standard errors:")
P.equation("gain_s = b_0 + sum_k b_k z_sk + e_s,   Var(b) = (Z'Z)^-1 Z' diag( e_s^2 / (1 - h_ss)^2 ) Z (Z'Z)^-1")
feats = list(PR["ols"])
P.table(["covariate", "std. beta", "p (HC3)", "RF permutation importance", "marginal Spearman rho"],
        [[f, round(PR["ols"][f]["beta_std"], 4), f"{PR['ols'][f]['p_hc3']:.2g}", round(PR["rf_perm_importance"][f], 3), round(PR["spearman_gain_vs"][f][0], 2)] for f in feats],
        f"Predictors of interaction gain (OLS R^2 = {PR['ols_r2']:.2f}; random forest 5-fold CV R^2 = {PR['rf_cv_r2_mean']:.2f}; results/predictors_audit.json).")
P.p("Network density is the strongest independent predictor, followed by beta dispersion and community size. Diversity, modularity, and the "
    "assembly and gut flags have sizeable marginal correlations but no independent effect once these are included. This is partly circular: "
    "the interaction model learns from the same co-occurrence structure that density summarises. We therefore offer density as a pre-fit "
    "diagnostic of whether a twin will gain from interactions, not as evidence that fitted interactions are causal.")

P.h("6. Negative results (kept by design)")
for t in [
    "gLV replicator 'beat' of cNODE on Drosophila (0.052) and soil in vitro under 10-fold CV was RETRACTED: under LOO it scores 0.074 and 0.099, worse than published cNODE (0.066, 0.079).",
    "Our cNODE re-implementation does not reproduce the published medians (e.g. Drosophila 0.104 vs 0.066), so all cNODE comparisons use published numbers.",
    "GraphTwin (attention GNN) never beat published cNODE on any dataset.",
    "An earlier claim that a population-mean null beats MDSINE2 on the healthy cohort came from flooring predictions at 1e5, a different metric; with the official metric MDSINE2 beats that unconditional null (1.061 vs 1.442). RETRACTED.",
    "Healthy cohort: RA-MDSINE2 without modules beats our forecaster under the official detected-only metric (0.883 vs 0.919, p = 0.045).",
    "Our own falsifiable prediction (Section 7, v1) that scoring all timepoints would erase the forecaster's advantage was FALSIFIED: under the all-timepoint metric it ranks first on both cohorts (UC 1.654 vs MDSINE2-NM 1.824; healthy 1.752 vs 2.072; results/mdsine2_headtohead_*_alltimepoints.json).",
    "The candidate 'human gut is least interaction-predictable' was rejected as confounded with assembly-derived data.",
    "Keystone consensus found only 2 of 248 genera at FDR < 0.05, both oral; there is no cross-biome keystone signal.",
    "Network modularity and Shannon diversity do not independently predict interaction gain.",
    "Keystone genera are not robustly over-represented in BugSigDB disease signatures (p = 0.062 with estimated dispersion).",
    "No GTDB family is enriched among keystones after FDR (best q = 0.71).",
    "Gram stain, motility, sporulation, GC content and doubling time do not track keystone frequency after BH.",
    "The anaerobe-keystone association does not pass FDR within any single biome (Oral, Plants, Insecta show near-zero or negative effects).",
    "The GAI effect failed under graphical lasso (p=0.15) and igraph betweenness (p=0.34); it is ridge-definition-specific. ProTraits failed its coverage gate (51 vs 100 genera).",
    "PubTator3 continuous oral literature fraction failed to replicate the HOMD oral-hub effect (gglasso p=0.57; igraph p=0.23). The HOMD effect remains list-specific, despite passing leave-one-family-out sensitivity.",
    "XGBoost added value relative to its reduced model but both absolute OOF R2 values were negative. A separate shallow LightGBM/CatBoost check has modest positive absolute R2; neither validates a causal relationship.",
    "Biopython Bio.Phylo found no unusual oral-genus clustering on the Open Tree synthetic topology (p=0.53).",
]:
    P.p("- " + t)

P.h("7. Discussion")
P.p("On these host-associated benchmark cohorts, a population prior is competitive with the reported interaction models. For cNODE the null interval contains the published error; for MDSINE2 it leads one cohort and ties another under the official metric. The all-timepoint check also favours it, despite our original prediction to the contrary.")
P.p("[v1 text, now tested and falsified - kept for the record] Falsifiable prediction. If the MDSINE2 metric is changed to score all timepoints (with an explicit detection model), the "
    "presence-conditional forecaster's advantage on UC should shrink or reverse. The all-timepoint test in Section 6 falsified that prediction: the forecaster remains ahead on the released source data. We retain the prediction for auditability, not as an open item.")
P.p("Practical recommendation. Benchmarks for microbiome twins should report a presence-conditional population baseline and score "
    "detection as well as abundance. Without both, accuracy numbers overstate what the interaction structure contributes.")
P.p("Limitations. Five UC mice and four healthy mice; 141-taxon selection by mean abundance approximates the paper's filter; "
    "cNODE comparisons rely on published point estimates; no per-timepoint MDSINE2 predictions.")

P.h("8. Tools used")
TL = _pd.read_csv("results/tools_ledger.csv"); TL["gate"] = TL.counts_for_gate.astype(str).map({"True": "counts", "False": "infra (excluded)"})
P.p("The program target of 40 counted external tools was reached with a margin; count the ledger entries marked True, not infrastructure. Tools include source databases and analytical libraries actually used in committed scripts. This count does not measure independence of biological evidence.")
P.table(["tool", "kind", "gate"], TL[["tool", "kind", "gate"]].values.tolist(),
        f"Tools ledger: {len(TL)} entries, {int((TL.gate == 'counts').sum())} counting toward the gate after excluding infrastructure.")

P.h("9. Reproducibility")
P.p("Repository: github.com/uditakankananonononono/mega27-04-microbiome-twin (private). Commands: python run_bench.py <dataset> "
    "presence_mean,cnode,glv,graphtwin 10; python bench_mdsine2.py healthy|uc; python -m pytest -q; python paper/build_paper.py.")

P.h("Appendix A. MGnify study accessions used")
P.table(["MGnify study", "INSDC project", "biome", "samples", "genera"],
        [[r.study, r.secondary_accession, r.biome.split(":")[-1], r.n_samples, r.n_genera] for r in MM.itertuples()],
        f"All {len(MM)} MGnify studies fetched and used (data/raw/mgnify/manifest.csv).")
P.h("References")
for r in [
    "Michel-Mata S, Wang X-W, Liu Y-Y, Angulo MT. Predicting microbiome compositions from species assemblages through deep learning. iMeta 2022. https://pmc.ncbi.nlm.nih.gov/articles/PMC9221840/",
    "Mitchell AL, et al. MGnify: the microbiome analysis resource in 2020. Nucleic Acids Res 2020.",
    "Gibson TE, Kim Y, Acharya S, et al. Learning ecosystem-scale dynamics from microbiome data with MDSINE2. Nature Microbiology 2025. https://www.nature.com/articles/s41564-025-02112-6",
    "Kanehisa M, Furumichi M, Sato Y, et al. KEGG for taxonomy-based analysis of pathways and genomes. Nucleic Acids Res 2023.",
    "Olson RD, Assaf R, Brettin T, et al. Introducing the Bacterial and Viral Bioinformatics Resource Center (BV-BRC). Nucleic Acids Res 2023.",
    "Madin JS, Nielsen DA, Brbic M, et al. A synthesis of bacterial and archaeal phenotypic trait data. Scientific Data 2020;7:170.",
    "Parks DH, Chuvochina M, Rinke C, et al. GTDB: an ongoing census of bacterial and archaeal diversity through a phylogenetically consistent, rank normalized and complete genome-based taxonomy. Nucleic Acids Res 2022.",
    "Bucci V, et al. MDSINE: Microbial Dynamical Systems INference Engine. Genome Biology 2016.",
    "Stein RR, et al. Ecological modeling from time-series inference: insight into dynamics and stability of intestinal microbiota. PLoS Comput Biol 2013.",
]:
    P.p(r)
P.save("paper/mega27-04-microbiome-twin-paper.docx")
print("ok", P.eq, "equations", P.tab, "tables", P.fig, "figures")
