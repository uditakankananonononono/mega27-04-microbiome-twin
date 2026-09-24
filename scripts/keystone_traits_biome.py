"""Falsification test of the anaerobe-keystone candidate within single biomes.
Per study: logistic GLM-free test - Mann-Whitney of genus anaerobe share, top vs non-top genera; then per biome
recompute genus frac_top and Spearman with anaerobe share. Also a study-stratified test: mean within-study difference
(top minus non-top anaerobe share), sign-flip permutation across studies. Output: results/keystone_traits_biome.json."""
import json, numpy as np, pandas as pd
from scipy.stats import spearmanr
T = pd.read_csv("results/keystone_traits.csv")[["genus", "anaerobe"]].dropna()
P = pd.read_csv("results/keystone_per_study.csv.gz").merge(T, on="genus")
out = {"n_rows": len(P), "n_studies": int(P.study.nunique()), "by_biome": {}}
for b, g in P.groupby("biome"):
    f = g.groupby("genus").agg(ft=("top", "mean"), n=("top", "size"), an=("anaerobe", "first")); f = f[f.n >= 3]
    if len(f) >= 15 and g.study.nunique() >= 3:
        rho, p = spearmanr(f.an, f.ft); out["by_biome"][b] = {"studies": int(g.study.nunique()), "genera": len(f), "rho": rho, "p": p}
d = P.groupby("study").apply(lambda g: g[g.top].anaerobe.mean() - g[~g.top].anaerobe.mean() if g.top.any() and (~g.top).any() else np.nan).dropna()
rng = np.random.default_rng(1); null = [(d.values * rng.choice([-1, 1], len(d))).mean() for _ in range(10000)]
out["within_study"] = {"n_studies": len(d), "mean_diff": d.mean(), "frac_positive": float((d > 0).mean()), "signflip_p": (1 + sum(abs(x) >= abs(d.mean()) for x in null)) / 10001}
for b in P.biome.unique():
    db = d[d.index.isin(P[P.biome == b].study.unique())]
    if len(db) >= 5:
        nb = [(db.values * rng.choice([-1, 1], len(db))).mean() for _ in range(5000)]
        out["within_study"][f"biome:{b}"] = {"n": len(db), "mean_diff": db.mean(), "p": (1 + sum(abs(x) >= abs(db.mean()) for x in nb)) / 5001}
json.dump(out, open("results/keystone_traits_biome.json", "w"), indent=1, default=float); print(json.dumps(out, indent=1, default=float))
