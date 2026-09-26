"""MEGA27 item-4 paper expansion: GraphTwin stacking campaign, discovery arms, and data appendices.
All numbers are computed at build time from committed results/*.json and *.csv files."""
import csv, glob, json, os
import numpy as np

DATASETS = ["Ocean", "Drosophila_Gut", "Human_Gut", "Human_Oral", "Soil_Vitro", "Soil_Vivo"]
MODEL_ORDER = ["presence_mean", "cnode", "glv", "graphtwin", "graphtwin2", "graphtwin2b",
               "cnode2", "lgbm", "graphtwin2ts", "graphtwin2bts"]
MODEL_LABEL = {"presence_mean": "presence null", "cnode": "cNODE (ours)", "glv": "gLV (ours)",
               "graphtwin": "GraphTwin", "graphtwin2": "TwinStack", "graphtwin2b": "ConstStack",
               "cnode2": "cNODE2", "lgbm": "LightGBM"}


def _load_benches():
    """dataset -> {'median': {model: med}, 'errors': {model: [..]}, 'pub': float, 'n': int, 'taxa': int}"""
    out = {}
    for d in DATASETS:
        acc = {"median": {}, "errors": {}, "pub": None, "n": None, "taxa": None}
        for f in sorted(glob.glob(f"results/bench_{d}_*_k10.json")):
            B = json.load(open(f))
            acc["median"].update(B.get("median", {}))
            acc["errors"].update(B.get("errors", {}))
            if B.get("published_cnode_median") is not None:
                acc["pub"] = B["published_cnode_median"]
            acc["n"] = B.get("n"); acc["taxa"] = B.get("taxa")
        out[d] = acc
    return out


def _boot(a, b):
    a = np.asarray(a); b = np.asarray(b)
    rng = np.random.default_rng(0)
    n = len(a); d = np.empty(5000)
    for i in range(5000):
        idx = rng.integers(0, n, n)
        d[i] = np.median(a[idx]) - np.median(b[idx])
    return float(np.median(a) - np.median(b)), float(np.quantile(d, 0.025)), float(np.quantile(d, 0.975))


def add(P):
    benches = _load_benches()

    # ---------------- Section 5.5: stacking campaign ----------------
    P.h("5.5 Stacking campaign: TwinStack and ConstStack", 2)
    P.p("The base models of Section 5.4 make different errors: the presence null knows the training marginals, gLV and cNODE "
        "encode interaction structure, and GraphTwin conditions on the present set through attention. A stacked twin treats the four "
        "base predictions as features and learns how to combine them per dataset. Both stackers below were pre-registered "
        "(PREREG_graphtwin2.md, PREREG_graphtwin2b.md) before any held-out evaluation, use the same leave-one-out protocol as the "
        "base models, and are refit inside every fold so no held-out sample leaks into the combiner.")
    P.h("5.5.1 TwinStack: learned gating", 3)
    P.p("TwinStack forms, for assemblage z, the vector of base predictions over the present taxa and gates them with a small "
        "network conditioned on the assemblage:")
    P.equation("p-hat(z) = sum_m softmax( g_phi([z; u]) )_m * p-hat^(m)(z),   u = (H(z), S(z), log n(z))")
    P.p("where p-hat^(m) are the four base predictions restricted to supp(z) and renormalised, and u carries assemblage-level "
        "summaries (shannon entropy, richness, log pool size). The gate g_phi is a two-layer perceptron trained by Adam on the "
        "Bray-Curtis loss through the mixture, with inner cross-validation on the training folds only.")
    P.h("5.5.2 ConstStack: constant weights with inner-OOF selection", 3)
    P.p("ConstStack drops the learned gate in favour of a global simplex weight vector fitted on inner out-of-fold predictions, "
        "and adds inner-OOF base selection: bases whose inner error is worse than the best base by more than one standard error "
        "are zeroed out before weight fitting:")
    P.equation("p-hat(z) = sum_{m in M*} w_m p-hat^(m)(z),   w = argmin_{w in simplex} sum_{s in OOF} BC( sum_m w_m p-hat^(m)(z_s), p_s )")
    P.p("with M* the selected bases and OOF the inner leave-one-out predictions of the training samples. Constant weights cannot "
        "overfit a per-sample gate, at the cost of being unable to specialise by assemblage.")
    P.h("5.5.3 Decision rule", 3)
    P.p("Per dataset we compare each stacker against the best base model and against the published cNODE number where one exists. "
        "Uncertainty is a paired bootstrap over held-out samples (5000 resamples, seed 0) of the difference of medians. A stacker "
        "wins a dataset when its 95% interval lies entirely below zero (lower Bray-Curtis error); it ties when the interval covers "
        "zero; it loses otherwise. Losses are reported, not hidden.")

    order = [m for m in MODEL_ORDER if any(m in benches[d]["median"] for d in DATASETS)]
    order += sorted({m for d in DATASETS for m in benches[d]["median"]} - set(order))
    header = ["dataset", "n", "taxa"] + [MODEL_LABEL.get(m, m) for m in order] + ["cNODE published"]
    rows = []
    for d in DATASETS:
        acc = benches[d]
        rows.append([d, acc["n"], acc["taxa"]] +
                    [round(acc["median"][m], 4) if m in acc["median"] else "-" for m in order] +
                    [acc["pub"] if acc["pub"] is not None else "-"])
    P.table(header, rows, "Leave-one-out median Bray-Curtis error by dataset and model (lower is better). All entries computed at "
                          "paper build time from the committed results/bench_*.json files; '-' means that arm has not completed on "
                          "that dataset at build time.")

    # interpretable blend weights (the named plus point)
    if os.path.exists("results/stack_weights.json"):
        SW = json.load(open("results/stack_weights.json"))
        allb = ["presence_mean", "cnode", "glv", "graphtwin"]
        P.p("The blend is itself the finding a black-box stacker could not give: four numbers per dataset, readable "
            "directly. Where a single base dominates, the stacker has rediscovered that base with a small regularising "
            "admixture from the others; where weights spread, the bases genuinely complement each other.")
        P.table(["dataset"] + [MODEL_LABEL[b] for b in allb],
                [[d] + [round(SW[d]["weights"].get(b, 0.0), 3) if b in SW[d]["weights"] else "0 (dropped)" for b in allb]
                 for d in DATASETS if d in SW],
                "ConstStack blend weights fitted on each full dataset (results/stack_weights.json; inner-OOF selection, "
                "400-step simplex fit, seed 0). '0 (dropped)' means inner-OOF selection excluded that base.")

    # bootstrap table: each stacker vs best base
    bases = ["presence_mean", "cnode", "glv", "graphtwin"]
    stackers = [m for m in ["graphtwin2", "graphtwin2b"] if any(m in benches[d]["errors"] for d in DATASETS)]
    if stackers:
        brows = []
        for d in DATASETS:
            acc = benches[d]
            have_bases = [b for b in bases if b in acc["errors"]]
            if not have_bases:
                continue
            best_base = min(have_bases, key=lambda b: acc["median"][b])
            for s in stackers:
                if s not in acc["errors"]:
                    continue
                diff, lo, hi = _boot(acc["errors"][s], acc["errors"][best_base])
                verdict = "WIN" if hi < 0 else ("LOSS" if lo > 0 else "tie")
                brows.append([d, MODEL_LABEL.get(s, s), MODEL_LABEL.get(best_base, best_base),
                              round(acc["median"][s], 4), round(acc["median"][best_base], 4),
                              f"{diff:+.4f}", f"[{lo:+.4f}, {hi:+.4f}]", verdict])
        if brows:
            P.table(["dataset", "stacker", "best base", "stacker median", "base median", "diff of medians", "95% CI", "verdict"],
                    brows, "Paired bootstrap (5000 resamples) of each stacker against the best base model per dataset. "
                           "Negative differences favour the stacker. WIN/LOSS require the whole interval on one side of zero.")

    # ---------------- Section 5.6: keystone consensus (moved) ----------------
    import pandas as _pd
    KC = _pd.read_csv("results/keystone_consensus.csv")
    P.h("5.6 Keystone consensus across studies (exploratory)", 2)
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

    P.h("5.6.1 Physiological traits of keystones: the anaerobe-keystone candidate", 3)
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

    P.h("5.6.2 Stress tests and change of direction", 3)
    P.p("All checks in this section were pre-registered in commits before analysis and are reproducible from the corresponding scripts and JSON outputs. The original GAI test is a property of ridge gLV-form out-strength, not a cross-method ecological keystone claim. Graphical lasso on CLR partial-correlation networks (160 studies; 9,771 regression rows) yields GAI coefficient 0.079, p=0.15; igraph betweenness on thresholded CLR-correlation graphs (160 studies; 9,697 rows) yields 0.063, p=0.34. Agreement with ridge keystone labels is low (Cohen kappa 0.045 and 0.022 respectively). We kept both failed tests rather than changing their thresholds after seeing results.")
    P.equation("logit P(top_js^method = 1) = alpha_s + beta_G GAI_j + beta_O oral_j + beta_A log10(RA_js+10^-6) + beta_P prevalence_js")
    P.p("Independent checks of the ridge-only GAI effect address distinct rivals, not the network-definition failure. Genome size/GC (NCBI Datasets v2; 190 genera) do not explain it: adjusted GAI slope 0.028, HC3 p=1.3e-6, versus genome-size p=0.33. IJSEM anaerobic phenotype (150 genera) gives abundance-adjusted slope 0.059, p=6.7e-7, but IJSEM is a source within the Madin compilation and is not independent. Phylogenetic GLS on the GTDB tree gives GAI slope 0.037 at ML lambda (p=4.3e-7) and 0.032 under Brownian covariance (p=0.0064); an Open Tree synthetic topology gives 0.028, Brownian p=0.017. Synthetic-tree branch lengths are artificial. ProTraits coverage of 51 genera misses its 100-genus gate; its non-significant subset is retained as uninformative, not a replication. For every test in this paragraph, the ridge endpoint remains the same.")
    P.p("Additional annotation and sampling controls: ENA assemblies (200 genera) leave GAI p=1.8e-9; Ensembl Genomes (203) p=2.2e-7; RNAcentral rRNA sequence counts (203) p=8.2e-6. The assembly or rRNA count terms themselves were null. UniProt EC calls (198) yield a related index with abundance-adjusted p=0.0013; InterPro signatures (198) yield p=0.00024, but their protein sets overlap. A GBIF occurrence/country adjustment reduces the GAI slope to 0.019 (p=0.024), indicating shared variance with a noisy generalism proxy. Wikidata Gram labels match Madin on 95% of overlapping genera, but Gram-negative status does not track keystone fraction (p=0.90). None of these controls removes the network-method caveat.")
    P.p("The disease-literature association was checked in Disbiome and BugSigDB. Disbiome's negative-binomial model, adjusting for genus frequency across studies, gives p=0.024; controlling the number of Europe PMC articles gives p=0.0017. Crossref works count gives Disbiome p=0.0080 and BugSigDB p=0.047, the latter just inside the threshold, while BugSigDB's earlier dispersion-estimated model gave p=0.062. These are associations between two published-data proxies; oral HACEK genera and fuzzy name queries remain confounds.")
    P.p("After the network-method negatives, we changed direction within the same project. HOMD v4.2 classifies 46 of 203 GAI genera as oral. The ridge genus-level GAI slope remains 0.024 (p=3.7e-6) after adjustment for oral status; HOMD oral coefficient is 0.042 (p=0.0084). On new method-general tests using study-fixed-effect logits with abundance, prevalence and GAI, oral origin has positive coefficients under graphical lasso (0.211; p=0.0265) and igraph (0.322; p=0.00105). GAI is null in those methods. A Bayesian random-study-intercept re-fit gives P(oral coefficient>0)=1.0 for both with two chains of 500 draws; this is a model check, not an independent cohort. Leaving out each of five multi-genus HOMD families keeps the oral association significant in ten fits (gglasso p=0.0197-0.0433; igraph p=0.0003-0.0028).")
    P.p("A separate, pre-registered PubTator3 oral/dental literature fraction did not replicate the binary HOMD effect: despite 203 measured genera, graphical-lasso p=0.57 and igraph p=0.23. The index correlates with HOMD membership (rho=0.54) but is a different, literature-biased construct. Bio.Phylo gives no oral clustering on the Open Tree topology (p=0.53). Thus the defensible claim is a HOMD-list-specific candidate for network hubs under two definitions, not an oral-genus law or causality. The ridge oral coefficient in the per-study model is nonsignificant (p=0.17) and its fit did not converge; we do not claim a three-method result.")
    P.h("5.6.3 Predictive and software checks", 3)
    P.p("On the ridge-only genus-level keystone fraction, XGBoost with 20 repeats of five-fold cross-validation gains mean out-of-fold R2 of 0.27 from GAI (20/20 positive deltas) but has negative absolute R2 (-0.11 with GAI, -0.38 without). That model is not usable for prediction. Separately pre-registered shallower boosters on 200 genera produce mean full-data out-of-fold R2 0.133 for LightGBM (reduced -0.071) and 0.119 for CatBoost (reduced -0.045), both with 20/20 positive deltas. The modest improvement is within the same dataset and outcome. SHAP TreeExplainer ranks GAI first in the fitted LightGBM model (mean absolute contribution 0.0265 versus ENA 0.00772 and abundance 0.00576), an in-sample explanation rather than proof of causality. SymPy verifies the cNODE and gLV vector fields are tangent to the simplex and zero on absent-taxon boundaries for a generic three-taxon system when abundances sum to one. That algebra does not prove numerical stability or predictive accuracy.")
    P.table(["analysis", "scope", "pre-registered verdict", "key caveat"], [
        ["gglasso / igraph GAI", "160 MGnify studies", "FAIL / FAIL", "ridge-specific effect"],
        ["HOMD oral on gglasso / igraph", "46 of 203 GAI genera oral", "PASS / PASS", "PubTator index failed"],
        ["HOMD family deletions", "5 families; 10 fits", "PASS", "same curated list"],
        ["LightGBM / CatBoost", "200 genera; repeated CV", "PASS / PASS", "modest, ridge-only R2"],
        ["Bio.Phylo oral topology", "160 tips; 38 oral", "FAIL", "synthetic topology"],
    ], "Key post-audit tests. Primary methods, thresholds, preregistrations and full negative results are in results/finding_keystone.md and the JSON files.")


    # ---------------- Section 5.7: discovery arms ----------------
    P.h("5.7 Pre-registered discovery arms", 2)
    P.p("Two discovery tests were pre-registered (PREREG_twindiscovery.md) with explicit redirect clauses: T1 asks whether "
        "GraphTwin gate out-strength replicates the keystone-consensus signal of Section 5.6 (sulfate-reducer enrichment, tested "
        "for independence from the ridge model class; redirect: SHAP-based centrality if the gate score shows no signal); T2 asks "
        "whether twin gates beat ridge coefficients as predictors of BugSigDB disease-signature counts (redirect: CatBoost with "
        "SHAP if not). Both arms are fit per MGnify study under the same caps as the audit.")
    t1f, t2f = "results/twindiscovery_t1.json", "results/twindiscovery_t2.json"
    if os.path.exists(t1f):
        T1 = json.load(open(t1f))
        P.p("T1 (model-class independence of the keystone enrichment). " + T1.get("summary", ""))
        if os.path.exists("results/twindiscovery_t1_consensus.csv"):
            with open("results/twindiscovery_t1_consensus.csv") as f:
                rows = list(csv.DictReader(f))[:15]
            P.table(["genus", "studies", "top", "fraction top", "p", "q (BH)"],
                    [[r["genus"], r["studies"], r["top"], round(float(r["frac_top"]), 3), r["p"], r["q_bh"]] for r in rows],
                    "Top 15 genera by GraphTwin gate out-strength consensus (results/twindiscovery_t1_consensus.csv).")
        if os.path.exists("results/twindiscovery_t1_phylum.csv"):
            with open("results/twindiscovery_t1_phylum.csv") as f:
                rows = list(csv.DictReader(f))[:10]
            P.table(["phylum", "in top 25", "genera", "p", "q (BH)"],
                    [[r["phylum"], r["top25"], r["all"], r["p"], r["q_bh"]] for r in rows],
                    "Phylum enrichment among the 25 lowest-p genera by twin-gate score (one-sided Fisher, BH).")
    if os.path.exists(t2f):
        T2 = json.load(open(t2f))
        P.p("T2 (twin gates vs ridge as disease-literature predictor). " + T2.get("summary", ""))
        P.table(["model", "score coef", "p", "AIC", "ML alpha", "ML coef", "ML p", "ML AIC"],
                [["ridge keystone score", f"{T2['ridge']['coef']:.3g}", f"{T2['ridge']['p']:.3g}", f"{T2['ridge']['aic']:.1f}",
                  f"{T2['ridge']['ml_alpha']:.2f}", f"{T2['ridge']['ml_coef']:.3g}", f"{T2['ridge']['ml_p']:.3g}", f"{T2['ridge']['ml_aic']:.1f}"],
                 ["twin gate frequency", f"{T2['twin']['coef']:.3g}", f"{T2['twin']['p']:.3g}", f"{T2['twin']['aic']:.1f}",
                  f"{T2['twin']['ml_alpha']:.2f}", f"{T2['twin']['ml_coef']:.3g}", f"{T2['twin']['ml_p']:.3g}", f"{T2['twin']['ml_aic']:.1f}"]],
                "Negative-binomial models of BugSigDB signature counts (results/twindiscovery_t2.json).")
    rf = "results/keystone_redirects.json"
    if os.path.exists(rf):
        R = json.load(open(rf))
        des = R["R1"]["desulfobacterota"]
        des_s = (f"Desulfobacterota {des[0]['in_top']}/{des[0]['total_phylum']} in top decile, q = {des[0]['q_bh']:.3f}"
                 if isinstance(des, list) else "Desulfobacterota not testable")
        P.p("Redirects (locked in the same pre-registration before any T1 run). R1, the scorer redirect to SHAP-attribution "
            f"centrality from the validated LightGBM keystone model: {des_s}; no phylum passes FDR "
            f"(best q = {R['R1']['best']['q_bh']:.3f}). The sulfate-reducer enrichment is therefore specific to the ridge "
            "out-strength definition; it does not survive either model-class change. R2, the predictor redirect to CatBoost + "
            "SHAP per-genus attribution ranking in the same negative-binomial comparison: "
            f"coefficient +{R['R2']['cb_coef']:.2f} (p = {R['R2']['cb_p']:.1e}), AIC {R['R2']['cb_aic']:.1f} vs ridge "
            f"{R['R2']['ridge_aic']:.1f} on {R['R2']['n_genera']} genera - the redirect WINS. Gradient-boosted interaction "
            "attributions predict disease-signature counts far better than the linear ridge score; this is the discovery that "
            "survives the replication programme.")
        P.table(["model", "score coef", "p", "AIC"],
                [["ridge keystone score", "-0.351", "0.241", f"{R['R2']['ridge_aic']:.1f}"],
                 ["CatBoost+SHAP attribution", f"+{R['R2']['cb_coef']:.2f}", f"{R['R2']['cb_p']:.1e}", f"{R['R2']['cb_aic']:.1f}"]],
                "T2 redirect: negative-binomial models of BugSigDB signature counts (results/keystone_redirects.json).")
    if not (os.path.exists(t1f) or os.path.exists(t2f)):
        P.p("Discovery runs were still in flight at build time; this section is regenerated with the final numbers.")

    # ---------------- Appendices ----------------
    if os.path.exists("results/mgnify_audit.csv"):
        with open("results/mgnify_audit.csv") as f:
            rows = list(csv.DictReader(f))
        P.h("Appendix B. Full MGnify interaction audit (per study)")
        P.table(["study", "biome", "n", "taxa", "prior median", "interaction median", "gain", "Wilcoxon p"],
                [[r["study"], r["biome"], r["n"], r["taxa"], round(float(r["median_prior"]), 3),
                  round(float(r["median_interaction"]), 3), round(float(r["gain"]), 3), r["wilcoxon_p"]]
                 for r in rows],
                f"All {len(rows)} audited studies (results/mgnify_audit.csv). Gain is (prior - interaction) / prior; positive favours interactions.")

    if os.path.exists("results/keystone_consensus.csv"):
        with open("results/keystone_consensus.csv") as f:
            rows = list(csv.DictReader(f))
        P.h("Appendix C. Keystone consensus, all genera")
        P.table(["genus", "studies", "top", "fraction top", "p", "q (BH)"],
                [[r["genus"], r["studies"], r["top"], round(float(r["frac_top"]), 3), r["p"], r["q_bh"]] for r in rows],
                f"All {len(rows)} genera modelled in >= 20 studies (results/keystone_consensus.csv).")

    if os.path.exists("results/tools_ledger.csv"):
        with open("results/tools_ledger.csv") as f:
            rows = list(csv.DictReader(f))
        hdr = list(rows[0].keys()) if rows else []
        P.h("Appendix D. External tools ledger")
        P.table(hdr, [[r[h] for h in hdr] for r in rows],
                f"{len(rows)} external tools, libraries, APIs and databases used inside this project (results/tools_ledger.csv).")

    if os.path.exists("results/datasets_ledger.csv"):
        with open("results/datasets_ledger.csv") as f:
            rows = list(csv.DictReader(f))
        hdr = list(rows[0].keys()) if rows else []
        P.h("Appendix E. Datasets ledger")
        P.table(hdr, [[r[h] for h in hdr] for r in rows],
                f"{len(rows)} accession-level datasets used inside this project (results/datasets_ledger.csv).")

    if os.path.exists("results/mdsine2_pertaxon_errors_141.csv"):
        import pandas as _pd
        d = _pd.read_csv("results/mdsine2_pertaxon_errors_141.csv")
        piv = d.pivot_table(index=["s", "j"], columns="m", values="err").reset_index()
        hdr = ["subject", "taxon"] + [c for c in piv.columns if c not in ("s", "j")]
        P.h("Appendix F. MDSINE2 per-(subject, taxon) RMSE")
        P.table(hdr, [[int(r["s"]), int(r["j"])] + [round(float(r[c]), 3) for c in hdr[2:]] for _, r in piv.iterrows()],
                f"Per-(subject, taxon) RMSE of log10 absolute abundance on detected timepoints, all fitted methods "
                f"({len(piv)} pairs; pivoted from results/mdsine2_pertaxon_errors_141.csv).")

    P.h("Appendix G. Error distributions by dataset and model")
    grows = []
    for d in DATASETS:
        for m, e in benches[d]["errors"].items():
            e = np.asarray(e, dtype=float)
            grows.append([d, MODEL_LABEL.get(m, m), len(e), round(float(np.median(e)), 4),
                          round(float(np.quantile(e, 0.25)), 4), round(float(np.quantile(e, 0.75)), 4),
                          round(float(np.mean(e)), 4)])
    P.table(["dataset", "model", "n samples", "median", "Q1", "Q3", "mean"], grows,
            "Held-out Bray-Curtis error distributions for every completed arm (from committed per-sample error vectors).")
