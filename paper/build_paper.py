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
P.p("Caveat that limits the claim. The official MDSINE2 metric scores only timepoints where the held-out taxon is detected. Our forecaster "
    "averages over training mice in which the taxon was detected, so it is tuned to exactly that conditional target. The UC result is a "
    "genuine beat under the published protocol, but it is also evidence that the protocol rewards detection-conditional averaging; it is "
    "not evidence that our model understands community dynamics better. We report it as a benchmark finding about the benchmark. "
    "Negative results are kept: our own graph network (GraphTwin), our gLV replicator and our cNODE re-implementation do not beat "
    "published cNODE under leave-one-out, and an earlier claimed gLV beat under 10-fold CV was retracted.")

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
P.p("All data are public, unmodified, and fetched by accession. Table 1 is the dataset manifest. We count nine distinct datasets. "
    "The program target of 120+ datasets was not reached, and we do not pad the count with sub-splits or derived tables.")
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

P.h("6. Negative results (kept by design)")
for t in [
    "gLV replicator 'beat' of cNODE on Drosophila (0.052) and soil in vitro under 10-fold CV was RETRACTED: under LOO it scores 0.074 and 0.099, worse than published cNODE (0.066, 0.079).",
    "Our cNODE re-implementation does not reproduce the published medians (e.g. Drosophila 0.104 vs 0.066), so all cNODE comparisons use published numbers.",
    "GraphTwin (attention GNN) never beat published cNODE on any dataset.",
    "An earlier claim that a population-mean null beats MDSINE2 on the healthy cohort came from flooring predictions at 1e5, a different metric; with the official metric MDSINE2 beats that unconditional null (1.061 vs 1.442). RETRACTED.",
    "Healthy cohort: RA-MDSINE2 without modules beats our forecaster (0.883 vs 0.919, p = 0.045).",
]:
    P.p("- " + t)

P.h("7. Discussion")
P.p("Two independent benchmarks point the same way: on host-associated communities, a well-built population prior sits at or near the "
    "state of the art. For cNODE this appears as a null whose interval contains the published error. For MDSINE2 it appears as a forecaster "
    "that tops one cohort and ties another, helped by a metric that only scores detected timepoints.")
P.p("Falsifiable prediction. If the MDSINE2 metric is changed to score all timepoints (with an explicit detection model), the "
    "presence-conditional forecaster's advantage on UC should shrink or reverse, because it predicts presence everywhere. We name this "
    "the detection-conditioning effect and quantify it as the change in rank under the two metrics. Testing this needs per-timepoint "
    "MDSINE2 predictions, which the Source Data does not include; it is the main open item.")
P.p("Practical recommendation. Benchmarks for microbiome twins should report a presence-conditional population baseline and score "
    "detection as well as abundance. Without both, accuracy numbers overstate what the interaction structure contributes.")
P.p("Limitations. Five UC mice and four healthy mice; 141-taxon selection by mean abundance approximates the paper's filter; "
    "cNODE comparisons rely on published point estimates; no per-timepoint MDSINE2 predictions.")

P.h("8. Tools used")
P.p("The program target of 40 external tools was not reached. Table 7 lists every tool actually used.")
P.table(["tool", "role"], [
    ["Python 3.10", "language"], ["NumPy", "arrays, bootstrap"], ["SciPy", "Wilcoxon, ODE integration"], ["pandas", "data loading"],
    ["PyTorch", "cNODE, gLV, GraphTwin training"], ["matplotlib", "figures"], ["pytest", "hermetic tests"], ["python-docx", "this paper"],
    ["cNODE repository (yixueyang/cNODE)", "data and reference protocol"],
    ["MDSINE2_Paper repository (gerberlab)", "data and official metric notebook"], ["git / GitHub", "version control"],
], "Tools table (honest count: 11).")

P.h("9. Reproducibility")
P.p("Repository: github.com/uditakankananonononono/mega27-04-microbiome-twin (private). Commands: python run_bench.py <dataset> "
    "presence_mean,cnode,glv,graphtwin 10; python bench_mdsine2.py healthy|uc; python -m pytest -q; python paper/build_paper.py.")

P.h("References")
for r in [
    "Michel-Mata S, Wang X-W, Liu Y-Y, Angulo MT. Predicting microbiome compositions from species assemblages through deep learning. iMeta 2022. https://pmc.ncbi.nlm.nih.gov/articles/PMC9221840/",
    "Gibson TE, Kim Y, Acharya S, et al. Learning ecosystem-scale dynamics from microbiome data with MDSINE2. Nature Microbiology 2025. https://www.nature.com/articles/s41564-025-02112-6",
    "Bucci V, et al. MDSINE: Microbial Dynamical Systems INference Engine. Genome Biology 2016.",
    "Stein RR, et al. Ecological modeling from time-series inference: insight into dynamics and stability of intestinal microbiota. PLoS Comput Biol 2013.",
]:
    P.p(r)
P.save("paper/mega27-04-microbiome-twin-paper.docx")
print("ok", P.eq, "equations", P.tab, "tables", P.fig, "figures")
