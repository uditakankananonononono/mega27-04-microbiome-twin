"""Run the interaction audit on every fetched MGnify study; resumable. Writes results/mgnify_audit.csv."""
import csv, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, "src")
from microtwin.audit import audit
OUT = "results/mgnify_audit.csv"
done = set(pd.read_csv(OUT).study) if os.path.exists(OUT) else set()
man = pd.read_csv("data/raw/mgnify/manifest.csv")
new = not os.path.exists(OUT); fh = open(OUT, "a", newline=""); w = csv.writer(fh)
if new: w.writerow(["study", "biome", "n", "taxa", "median_prior", "median_interaction", "gain", "int_better_frac", "wilcoxon_p"])
for _, r in man.iterrows():
    if r.study in done or not isinstance(r.file, str): continue
    X = pd.read_csv(r.file, sep="\t", index_col=0).T
    X = X.loc[X.sum(1) > 0]; X = X.loc[:, (X > 0).mean(0) >= 0.05]; X = X.loc[X.sum(1) > 0]
    if X.shape[1] > 150: X = X[X.columns[np.argsort(-(X > 0).mean(0).values)[:150]]]; X = X.loc[X.sum(1) > 0]  # top-150 genera by prevalence (O(N^4) ridge cost)
    if len(X) > 400: X = X.sample(400, random_state=0)  # cap for the 2 GB sandbox; recorded in n
    try:
        a = audit(X.values, k=5, seed=0)
    except Exception as e:
        print("fail", r.study, e, flush=True); continue
    w.writerow([r.study, r.biome, a["n"], a["taxa"], a["median_prior"], a["median_interaction"], a["gain"], a["int_better_frac"], a["wilcoxon_p"]]); fh.flush()
    print(r.study, r.biome.split(":")[-1], a["n"], a["taxa"], round(a["gain"], 4), "%.2g" % a["wilcoxon_p"], flush=True)
