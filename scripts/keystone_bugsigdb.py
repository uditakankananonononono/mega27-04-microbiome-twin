"""Do keystone-consensus genera appear more often in published differential-abundance signatures (BugSigDB) than expected
from how widespread they are? Negative-binomial GLM (statsmodels): n_signatures ~ keystone score + log(studies modelled).
Keystone score = -log10 binomial p from results/keystone_consensus.csv. Outputs: results/keystone_bugsigdb.csv, results/keystone_bugsigdb.json."""
import json, re
import numpy as np, pandas as pd
import statsmodels.api as sm
from scipy.stats import spearmanr
cnt = {}
for line in open("data/ref/bugsigdb_signatures_genus_taxname.gmt"):
    if line.startswith("#"): continue
    f = line.rstrip("\n").split("\t")
    for g in set(f[2:]): cnt[g] = cnt.get(g, 0) + 1
n_sig = sum(1 for l in open("data/ref/bugsigdb_signatures_genus_taxname.gmt") if not l.startswith("#"))
K = pd.read_csv("results/keystone_consensus.csv"); K["genus_clean"] = K.genus.str.replace(r"^[a-z]__", "", regex=True).str.strip()
K["bugsigdb_signatures"] = K.genus_clean.map(cnt).fillna(0).astype(int); K["kscore"] = -np.log10(K.p)
K.to_csv("results/keystone_bugsigdb.csv", index=False)
X = sm.add_constant(pd.DataFrame({"kscore": K.kscore, "log_studies": np.log(K.studies)}))
nb = sm.GLM(K.bugsigdb_signatures, X, family=sm.families.NegativeBinomial(alpha=1.0)).fit()
nb2 = sm.NegativeBinomial(K.bugsigdb_signatures, X).fit(disp=0)  # alpha estimated by ML
top2 = K.nsmallest(2, "p")[["genus_clean", "bugsigdb_signatures"]].values.tolist()
out = {"n_signatures_in_bugsigdb": n_sig, "n_genera": int(len(K)), "n_genera_in_bugsigdb": int((K.bugsigdb_signatures > 0).sum()),
       "nb_coef_kscore": float(nb.params["kscore"]), "nb_p_kscore": float(nb.pvalues["kscore"]),
       "nb_coef_log_studies": float(nb.params["log_studies"]), "nb_p_log_studies": float(nb.pvalues["log_studies"]),
       "spearman_kscore_vs_signatures": [float(x) for x in spearmanr(K.kscore, K.bugsigdb_signatures)], "fdr_keystones": top2,
       "nb_ml_alpha": float(nb2.params["alpha"]), "nb_ml_coef_kscore": float(nb2.params["kscore"]), "nb_ml_p_kscore": float(nb2.pvalues["kscore"]),
       "median_signatures_all": float(K.bugsigdb_signatures.median())}
json.dump(out, open("results/keystone_bugsigdb.json", "w"), indent=1); print(json.dumps(out, indent=1))
