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
          "MEGA-PROGRAM-27, Item 4 - Udita Phookan (program owner); computational work by an AI research agent. Draft of 24 September 2026.")

P.h("Abstract")
P.p("A microbiome digital twin is a model that, given what we know about a community, predicts what it will look like: its steady-state "
    "composition after assembly, or its trajectory under perturbation. Two leading published approaches are compositional neural ODEs "
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
P.p("We test that premise on the two public benchmarks that define the state of the art for the two main twin tasks. Our contributions are: "
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
P.p("All data are public, unmodified, and fetched by accession. Table 1 is the dataset manifest. We count 169 distinct accession-level datasets: the nine below plus 160 MGnify studies (Appendix A).")
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
]:
    P.p("- " + t)

P.h("7. Discussion")
P.p("Two independent benchmarks point the same way: on host-associated communities, a well-built population prior sits at or near the "
    "state of the art. For cNODE this appears as a null whose interval contains the published error. For MDSINE2 it appears as a forecaster "
    "that tops one cohort and ties another, helped by a metric that only scores detected timepoints.")
P.p("[v1 text, now tested and falsified - kept for the record] Falsifiable prediction. If the MDSINE2 metric is changed to score all timepoints (with an explicit detection model), the "
    "presence-conditional forecaster's advantage on UC should shrink or reverse, because it predicts presence everywhere. We name this "
    "the detection-conditioning effect and quantify it as the change in rank under the two metrics. Testing this needs per-timepoint "
    "MDSINE2 predictions, which the Source Data does not include; it is the main open item.")
P.p("Practical recommendation. Benchmarks for microbiome twins should report a presence-conditional population baseline and score "
    "detection as well as abundance. Without both, accuracy numbers overstate what the interaction structure contributes.")
P.p("Limitations. Five UC mice and four healthy mice; 141-taxon selection by mean abundance approximates the paper's filter; "
    "cNODE comparisons rely on published point estimates; no per-timepoint MDSINE2 predictions.")

P.h("8. Tools used")
TL = _pd.read_csv("results/tools_ledger.csv"); TL["gate"] = TL.counts_for_gate.astype(str).map({"True": "counts", "False": "infra (excluded)"})
P.p("The program target of 40 external tools was not reached. The table lists every tool actually used, from results/tools_ledger.csv.")
P.table(["tool", "kind", "where used", "gate"], TL[["tool", "kind", "where_used", "gate"]].values.tolist(),
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
    "Bucci V, et al. MDSINE: Microbial Dynamical Systems INference Engine. Genome Biology 2016.",
    "Stein RR, et al. Ecological modeling from time-series inference: insight into dynamics and stability of intestinal microbiota. PLoS Comput Biol 2013.",
]:
    P.p(r)
P.save("paper/mega27-04-microbiome-twin-paper.docx")
print("ok", P.eq, "equations", P.tab, "tables", P.fig, "figures")
