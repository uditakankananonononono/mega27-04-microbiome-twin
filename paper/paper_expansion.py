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

    # ---------------- Section 5.6: stacking campaign ----------------
    P.h("5.6 Stacking campaign: TwinStack and ConstStack", 2)
    P.p("The base models of Section 5.1 make different errors: the presence null knows the training marginals, gLV and cNODE "
        "encode interaction structure, and GraphTwin conditions on the present set through attention. A stacked twin treats the four "
        "base predictions as features and learns how to combine them per dataset. Both stackers below were pre-registered "
        "(PREREG_graphtwin2.md, PREREG_graphtwin2b.md) before any held-out evaluation, use the same leave-one-out protocol as the "
        "base models, and are refit inside every fold so no held-out sample leaks into the combiner.")
    P.h("5.6.1 TwinStack: learned gating", 3)
    P.p("TwinStack forms, for assemblage z, the vector of base predictions over the present taxa and gates them with a small "
        "network conditioned on the assemblage:")
    P.equation("p-hat(z) = sum_m softmax( g_phi([z; u]) )_m * p-hat^(m)(z),   u = (H(z), S(z), log n(z))")
    P.p("where p-hat^(m) are the four base predictions restricted to supp(z) and renormalised, and u carries assemblage-level "
        "summaries (shannon entropy, richness, log pool size). The gate g_phi is a two-layer perceptron trained by Adam on the "
        "Bray-Curtis loss through the mixture, with inner cross-validation on the training folds only.")
    P.h("5.6.2 ConstStack: constant weights with inner-OOF selection", 3)
    P.p("ConstStack drops the learned gate in favour of a global simplex weight vector fitted on inner out-of-fold predictions, "
        "and adds inner-OOF base selection: bases whose inner error is worse than the best base by more than one standard error "
        "are zeroed out before weight fitting:")
    P.equation("p-hat(z) = sum_{m in M*} w_m p-hat^(m)(z),   w = argmin_{w in simplex} sum_{s in OOF} BC( sum_m w_m p-hat^(m)(z_s), p_s )")
    P.p("with M* the selected bases and OOF the inner leave-one-out predictions of the training samples. Constant weights cannot "
        "overfit a per-sample gate, at the cost of being unable to specialise by assemblage.")
    P.h("5.6.3 Decision rule", 3)
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

    # ---------------- Section 5.7: discovery arms ----------------
    P.h("5.7 Pre-registered discovery arms", 2)
    P.p("Two discovery tests were pre-registered (PREREG_twindiscovery.md) with explicit redirect clauses: T1 asks whether "
        "GraphTwin gate out-strength replicates the keystone-consensus signal of Section 5.4 (sulfate-reducer enrichment, tested "
        "for independence from the ridge model class; redirect: SHAP-based centrality if the gate score shows no signal); T2 asks "
        "whether twin gates beat ridge coefficients as predictors of BugSigDB disease-signature counts (redirect: CatBoost with "
        "SHAP if not). Both arms are fit per MGnify study under the same caps as the audit.")
    t1f, t2f = "results/twindiscovery_t1.json", "results/twindiscovery_t2.json"
    if os.path.exists(t1f):
        T1 = json.load(open(t1f))
        P.p("T1 result: " + T1.get("summary", "see results/twindiscovery_t1.json"))
    if os.path.exists(t2f):
        T2 = json.load(open(t2f))
        P.p("T2 result: " + T2.get("summary", "see results/twindiscovery_t2.json"))
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
