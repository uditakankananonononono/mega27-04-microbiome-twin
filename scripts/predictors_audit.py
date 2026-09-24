"""What predicts where species-interaction models beat the population prior across 160 MGnify studies?
Per-study covariates: alpha diversity (scikit-bio Shannon), beta dispersion (scikit-bio Bray-Curtis), co-occurrence network density and
modularity (networkx), sample count, taxa count, assembly-derived flag, human-gut flag.
Models: statsmodels OLS with HC3 robust SEs on the audit gain; scikit-learn random forest with 5-fold CV R^2 and permutation importance.
Outputs: results/predictors_covariates.csv, results/predictors_audit.json."""
import json, warnings
import numpy as np, pandas as pd
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities, modularity
from scipy.stats import spearmanr
from skbio.diversity import alpha_diversity, beta_diversity
import statsmodels.api as sm
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold, cross_val_score
from sklearn.inspection import permutation_importance
warnings.filterwarnings("ignore")
A = pd.read_csv("results/mgnify_audit_fdr.csv"); M = pd.read_csv("data/raw/mgnify/manifest.csv")
rows = []
for _, r in A.iterrows():
    m = M[M.study == r.study].iloc[0]
    X = pd.read_csv(m.file, sep="\t", index_col=0).T
    X = X.loc[X.sum(1) > 0]
    counts = X.values.astype(int)
    sh = alpha_diversity("shannon", counts).mean()
    rich = (counts > 0).sum(1).mean()
    sub = counts[np.random.default_rng(0).choice(len(counts), min(len(counts), 200), replace=False)]
    bd = beta_diversity("braycurtis", sub).condensed_form().mean()
    P = X.div(X.sum(1), axis=0); prev = P.columns[(P > 0).mean() >= 0.2]
    G = nx.Graph(); G.add_nodes_from(prev)
    if len(prev) >= 3:
        rho = spearmanr(P[prev].values).statistic
        rho = np.atleast_2d(rho)
        for i in range(len(prev)):
            for j in range(i + 1, len(prev)):
                if abs(rho[i, j]) > 0.3: G.add_edge(prev[i], prev[j])
    dens = nx.density(G) if len(prev) >= 2 else 0.0
    if G.number_of_edges() > 0:
        C = greedy_modularity_communities(G); mod = modularity(G, C)
    else: mod = 0.0
    rows.append({"study": r.study, "gain": r.gain, "int_wins": bool(r.int_wins), "n": r.n, "taxa": r.taxa, "shannon": sh, "richness": rich,
                 "beta_bc": bd, "net_density": dens, "net_modularity": mod, "n_prevalent": len(prev),
                 "assembly": "assembl" in str(m.study_name).lower(), "human_gut": "Human:Digestive" in r.biome})
D = pd.DataFrame(rows); D.to_csv("results/predictors_covariates.csv", index=False)
feats = ["shannon", "beta_bc", "net_density", "net_modularity", "n", "taxa", "assembly", "human_gut"]
Xf = D[feats].astype(float).copy(); Xf["n"] = np.log(Xf.n); Xf["taxa"] = np.log(Xf.taxa)
Z = (Xf - Xf.mean()) / Xf.std()
ols = sm.OLS(D.gain, sm.add_constant(Z)).fit(cov_type="HC3")
rf = RandomForestRegressor(n_estimators=400, min_samples_leaf=5, random_state=0)
cv = cross_val_score(rf, Xf, D.gain, cv=KFold(5, shuffle=True, random_state=0), scoring="r2")
rf.fit(Xf, D.gain); pi = permutation_importance(rf, Xf, D.gain, n_repeats=30, random_state=0)
out = {"n_studies": int(len(D)), "ols_r2": float(ols.rsquared), "ols": {k: {"beta_std": float(ols.params[k]), "p_hc3": float(ols.pvalues[k])} for k in feats},
       "rf_cv_r2_mean": float(cv.mean()), "rf_cv_r2_folds": [float(x) for x in cv],
       "rf_perm_importance": {f: float(v) for f, v in zip(feats, pi.importances_mean)},
       "spearman_gain_vs": {f: [float(x) for x in spearmanr(D.gain, Xf[f])] for f in feats}}
json.dump(out, open("results/predictors_audit.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ["n_studies", "ols_r2", "rf_cv_r2_mean"]}))
for f in feats: print(f, round(out["ols"][f]["beta_std"], 4), f"{out['ols'][f]['p_hc3']:.2g}", round(out["rf_perm_importance"][f], 4), [round(x, 3) for x in out["spearman_gain_vs"][f]])
