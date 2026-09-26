"""Prereg redirect (PREREG_twindiscovery.md, locked before T1 ran):
R1 (T1 null): scorer redirects to SHAP-attribution centrality from the validated
LightGBM keystone model (keystone_shap.py, SH1 PASS). Per-genus score = signed SHAP
value of the GAI feature; top-decile genera -> same Fisher/binomial enrichment
construction as keystone_mgnify.py against GTDB v232 phyla (results/keystone_gtdb.csv).
R2 (T2 loss): predictor redirects to CatBoost + SHAP per-genus attribution ranking
(keystone_boosters.py, B1 PASS) as the score in the same NB-GLM comparison vs ridge
(n_signatures ~ score + log(studies); twin/catboost wins iff coef positive p<0.05 AND
AIC beats the ridge model's). All phyla tested; nothing hidden; negatives reported.
"""
import json, sys
import numpy as np, pandas as pd
import shap, statsmodels.api as sm
from scipy.stats import fisher_exact
sys.path.insert(0, "scripts")
from keystone_boosters import data, model

M = data()  # 200 genera: genus, genus_clean, frac_top, GAI, lra, log_ena, ...
FEATS = ["GAI", "lra", "log_ena"]
X = M[FEATS].to_numpy(); y = M.frac_top.to_numpy()
GT = pd.read_csv("results/keystone_gtdb.csv")[["genus", "gtdb_phylum"]]
M = M.merge(GT, on="genus", how="left")

def shap_scores(kind):
    m = model(kind, 0); m.fit(X, y)
    V = np.asarray(shap.TreeExplainer(m).shap_values(X))
    return V[:, 0]  # signed GAI attribution per genus

def bh(pvals):
    p = np.asarray(pvals); o = np.argsort(p); q = np.empty(len(p))
    q[o] = np.minimum.accumulate((p[o] * len(p) / np.arange(1, len(p) + 1))[::-1])[::-1]
    return np.minimum(q, 1)

def enrichment(score, label):
    thr = np.quantile(score, 0.9); top = score >= thr
    phyla = sorted(M.gtdb_phylum.dropna().unique()); rows = []
    for ph in phyla:
        is_ph = (M.gtdb_phylum == ph).to_numpy()
        a, b = int((is_ph & top).sum()), int((is_ph & ~top).sum())
        c, d = int((~is_ph & top).sum()), int((~is_ph & ~top).sum())
        if a == 0: continue
        _, p = fisher_exact([[a, b], [c, d]], alternative="greater")
        rows.append({"phylum": ph, "in_top": a, "total_phylum": a + b, "p": p})
    R = pd.DataFrame(rows)
    R["q_bh"] = bh(R.p) if len(R) else []
    R = R.sort_values("p")
    R.to_csv(f"results/redirect_{label}_enrichment.csv", index=False)
    des = R[R.phylum == "Desulfobacterota"]
    return {"scorer": label, "n_genera": int(len(M)), "n_top": int(top.sum()),
            "top_genera": list(M.genus[top].head(25)),
            "desulfobacterota": (des.to_dict("records") or "not testable (0 in top decile)"),
            "best": R.iloc[0].to_dict() if len(R) else None,
            "pass": bool((R.q_bh < 0.05).any())}

out = {}
# R1: LightGBM SHAP centrality (T1 redirect)
out["R1"] = enrichment(shap_scores("lightgbm"), "lgbm_shap")
print("R1:", json.dumps(out["R1"]["desulfobacterota"]), "best:", out["R1"]["best"], "pass:", out["R1"]["pass"])

# R2: CatBoost SHAP as BugSigDB predictor (T2 redirect)
score = shap_scores("catboost")
out["R2_enrichment"] = enrichment(score, "catboost_shap")  # same construction, reported too
B = pd.read_csv("results/keystone_bugsigdb.csv")  # genus_clean, bugsigdb_signatures, kscore, studies
J = pd.DataFrame({"genus_clean": M.genus_clean, "cb_shap": score}).merge(B, on="genus_clean", how="inner")
yy = J.bugsigdb_signatures.to_numpy()
def fit(feats):
    XX = sm.add_constant(J[feats])
    g = sm.GLM(yy, XX, family=sm.families.NegativeBinomial(alpha=1.0)).fit()
    return g
g_cb = fit(["cb_shap"]); g_ridge = fit(["kscore"])
coef, pv = g_cb.params["cb_shap"], g_cb.pvalues["cb_shap"]
out["R2"] = {"n_genera": int(len(J)), "cb_coef": float(coef), "cb_p": float(pv),
             "cb_aic": float(g_cb.aic), "ridge_aic": float(g_ridge.aic),
             "catboost_wins": bool(coef > 0 and pv < 0.05 and g_cb.aic < g_ridge.aic)}
print("R2:", json.dumps(out["R2"]))
json.dump(out, open("results/keystone_redirects.json", "w"), indent=1)
