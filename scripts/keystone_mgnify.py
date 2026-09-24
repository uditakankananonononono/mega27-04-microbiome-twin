"""Keystone-genus consensus from the interaction models fitted per MGnify study.
For each study: fit the steady-state gLV-form ridge model (lambda = median of the audit's CV choices, 100) on all samples,
build a directed graph with edge j->i weight |W_ij| (networkx), score genus j by out-strength centrality.
A genus is 'top' in a study if its out-strength is in the study's top 10%. Consensus = fraction of studies (where the
genus is modelled) in which it is top, compared with the 10% expected by chance (binomial test, BH-FDR).
"""
import json, sys
import numpy as np, pandas as pd, networkx as nx
from scipy.stats import binomtest
sys.path.insert(0, "src")
from microtwin.audit import fit_interaction
man = pd.read_csv("data/raw/mgnify/manifest.csv"); rows = []
for r in man.itertuples():
    X = pd.read_csv(r.file, sep="\t", index_col=0).T
    X = X.loc[X.sum(1) > 0]; X = X.loc[:, (X > 0).mean(0) >= 0.05]; X = X.loc[X.sum(1) > 0]
    if X.shape[1] > 150: X = X[X.columns[np.argsort(-(X > 0).mean(0).values)[:150]]]; X = X.loc[X.sum(1) > 0]
    if len(X) > 400: X = X.sample(400, random_state=0)
    P = X.values / X.values.sum(1, keepdims=True)
    mu, b, W = fit_interaction(P, 100.0)
    G = nx.DiGraph(); names = list(X.columns)
    for i in range(len(names)):
        for j in range(len(names)):
            if i != j and W[i, j] != 0: G.add_edge(names[j], names[i], weight=abs(W[i, j]))
    out = dict(G.out_degree(weight="weight")); s = pd.Series({n: out.get(n, 0.0) for n in names})
    thr = s.quantile(0.9)
    for n, v in s.items(): rows.append((r.study, r.biome.split(":")[-1], n, v, v >= thr))
    print(r.study, len(names), flush=True)
D = pd.DataFrame(rows, columns=["study", "biome", "genus", "out_strength", "top"]); D.to_csv("results/keystone_per_study.csv.gz", index=False)
g = D.groupby("genus").agg(studies=("study", "nunique"), top=("top", "sum")).reset_index(); g = g[g.studies >= 20]
g["frac_top"] = g.top / g.studies; g["p"] = [binomtest(int(t), int(n), 0.1, alternative="greater").pvalue for t, n in zip(g.top, g.studies)]
o = np.argsort(g.p.values); m = len(g); q = np.empty(m); q[o] = np.minimum.accumulate((g.p.values[o] * m / np.arange(1, m + 1))[::-1])[::-1]
g["q_bh"] = np.minimum(q, 1); g = g.sort_values("p"); g.to_csv("results/keystone_consensus.csv", index=False)
print(g.head(15).to_string(index=False))
