"""T2 (PREREG_twindiscovery.md): twin gates vs ridge as BugSigDB disease-signature predictor.
NB-GLM n_signatures ~ score + log(studies), score = twin-gate out-strength top-frequency
(results/twindiscovery_t1_consensus.csv), against the locked ridge model (results/keystone_bugsigdb.csv).
Twin wins iff its coefficient is positive with p < 0.05 AND model AIC beats the ridge model's.
Both GLM (alpha=1) and ML-estimated alpha variants are fit, mirroring keystone_bugsigdb.py."""
import json, sys
import numpy as np, pandas as pd
import statsmodels.api as sm

R = pd.read_csv("results/keystone_bugsigdb.csv")  # genus_clean, bugsigdb_signatures, kscore, studies
T = pd.read_csv("results/twindiscovery_t1_consensus.csv")  # genus, studies, top, frac_top, p, q_bh
T["genus_clean"] = T.genus.str.replace(r"^[a-z]__", "", regex=True).str.strip()
M = R.merge(T[["genus_clean", "frac_top", "studies"]].rename(columns={"studies": "twin_studies"}), on="genus_clean", how="inner")
y = M.bugsigdb_signatures

def fit(feats):
    X = sm.add_constant(M[feats])
    g = sm.GLM(y, X, family=sm.families.NegativeBinomial(alpha=1.0)).fit()
    m = sm.NegativeBinomial(y, X).fit(disp=0)
    return g, m

M["log_studies"] = np.log(M.studies); M["twin_freq"] = M.frac_top_y; M["log_twin_studies"] = np.log(M.twin_studies)
g_r, m_r = fit(["kscore", "log_studies"])
g_t, m_t = fit(["twin_freq", "log_twin_studies"])

win = (g_t.params["twin_freq"] > 0 and g_t.pvalues["twin_freq"] < 0.05 and g_t.aic < g_r.aic)
out = {"n_genera_merged": int(len(M)),
       "ridge": {"coef": float(g_r.params["kscore"]), "p": float(g_r.pvalues["kscore"]), "aic": float(g_r.aic),
                 "ml_alpha": float(m_r.params["alpha"]), "ml_coef": float(m_r.params["kscore"]), "ml_p": float(m_r.pvalues["kscore"]), "ml_aic": float(m_r.aic)},
       "twin": {"coef": float(g_t.params["twin_freq"]), "p": float(g_t.pvalues["twin_freq"]), "aic": float(g_t.aic),
                "ml_alpha": float(m_t.params["alpha"]), "ml_coef": float(m_t.params["twin_freq"]), "ml_p": float(m_t.pvalues["twin_freq"]), "ml_aic": float(m_t.aic)},
       "t2_pass": bool(win), "summary": ""}
out["summary"] = (f"T2: {out['n_genera_merged']} genera. Twin-gate coef {out['twin']['coef']:.3g} (p={out['twin']['p']:.3g}), "
                  f"AIC {out['twin']['aic']:.1f} vs ridge {out['ridge']['aic']:.1f}. "
                  f"{'TWIN WINS' if win else 'TWIN DOES NOT WIN - redirect to CatBoost+SHAP per pre-reg'}")
json.dump(out, open("results/twindiscovery_t2.json", "w"), indent=1)
M.to_csv("results/twindiscovery_t2_merged.csv", index=False)
print(out["summary"])
