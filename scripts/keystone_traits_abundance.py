"""Abundance/prevalence confound for the anaerobe-keystone candidate.
Recompute, with the exact filtering of keystone_mgnify.py, each genus's mean relative abundance and prevalence per study;
then within-study models of top-keystone status:
 (1) logistic GLM top ~ anaerobe + log10(mean abundance) + prevalence + C(study) (study fixed effects, cluster-robust SE by study);
 (2) same without anaerobe, to report the abundance-only effect.
Output: results/keystone_traits_abundance.json, results/keystone_genus_abundance.csv.gz"""
import json, numpy as np, pandas as pd, statsmodels.formula.api as smf
man = pd.read_csv("data/raw/mgnify/manifest.csv"); rows = []
for r in man.itertuples():
    X = pd.read_csv(r.file, sep="\t", index_col=0).T
    X = X.loc[X.sum(1) > 0]; X = X.loc[:, (X > 0).mean(0) >= 0.05]; X = X.loc[X.sum(1) > 0]
    if X.shape[1] > 150: X = X[X.columns[np.argsort(-(X > 0).mean(0).values)[:150]]]; X = X.loc[X.sum(1) > 0]
    if len(X) > 400: X = X.sample(400, random_state=0)
    P = X.div(X.sum(1), axis=0)
    for g in X.columns: rows.append((r.study, g, P[g].mean(), (X[g] > 0).mean()))
A = pd.DataFrame(rows, columns=["study", "genus", "mean_ra", "prevalence"]); A.to_csv("results/keystone_genus_abundance.csv.gz", index=False)
K = pd.read_csv("results/keystone_per_study.csv.gz").merge(A, on=["study", "genus"])
T = pd.read_csv("results/keystone_traits.csv")[["genus", "anaerobe"]].dropna()
D = K.merge(T, on="genus"); D["lra"] = np.log10(D.mean_ra + 1e-6); D["top"] = D.top.astype(int)
D = D[D.groupby("study").top.transform("sum") > 0]
out = {"n_rows": len(D), "n_studies": int(D.study.nunique()),
       "corr_anaerobe_lra": float(D[["anaerobe", "lra"]].corr().iloc[0, 1]), "corr_anaerobe_prev": float(D[["anaerobe", "prevalence"]].corr().iloc[0, 1])}
for name, f in [("full", "top ~ anaerobe + lra + prevalence + C(study)"), ("no_abund", "top ~ anaerobe + C(study)"), ("abund_only", "top ~ lra + prevalence + C(study)")]:
    m = smf.logit(f, D).fit(disp=0, cov_type="cluster", cov_kwds={"groups": pd.factorize(D.study)[0]}, maxiter=200)
    keep = [k for k in m.params.index if not k.startswith("C(")]
    out[name] = {"coef": m.params[keep].to_dict(), "p": m.pvalues[keep].to_dict(), "llf": m.llf}
json.dump(out, open("results/keystone_traits_abundance.json", "w"), indent=1); print(json.dumps(out, indent=1))
