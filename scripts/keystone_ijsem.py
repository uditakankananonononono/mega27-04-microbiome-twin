"""Pre-registered (results/preregistration_ijsem.md) IJSEM check of anaerobe-keystone.
Source: figshare 4272392 IJSEM_pheno_db_v1.0.txt (https://ndownloader.figshare.com/files/6994457). The oxygen field is named
'oxygen preference' in the file (pre-reg called it 'Oxygen'); coding as pre-registered: anaerobic=1; aerobic, facultative anaerobe,
facultative aerobe, microaerophile=0."""
import json, numpy as np, pandas as pd, statsmodels.api as sm
from scipy.stats import spearmanr
CODE = {"anaerobic": 1, "aerobic": 0, "facultative anaerobe": 0, "facultative aerobe": 0, "microerophile": 0}

def genus_anaerobe(df):
    d = df.dropna(subset=["oxygen preference", "Genus name"]).copy()
    d["an"] = d["oxygen preference"].str.strip().map(CODE); d = d.dropna(subset=["an"])
    d["genus"] = d["Genus name"].str.strip().str.capitalize()
    return d.groupby("genus").an.agg(["mean", "size"]).rename(columns={"mean": "ijsem_anaerobe", "size": "n_records"})

if __name__ == "__main__":
    ij = genus_anaerobe(pd.read_csv("data/ijsem/IJSEM_pheno_db_v1.0.txt", sep="\t", encoding="latin1"))
    K = pd.read_csv("results/keystone_kegg_genus.csv").drop_duplicates("genus_clean")
    ab = pd.read_csv("results/keystone_genus_abundance.csv.gz").groupby("genus").mean_ra.mean().rename("mean_ra")
    M = K.merge(ij, left_on="genus_clean", right_index=True).merge(ab, left_on="genus_clean", right_index=True, how="left")
    rho, p2 = spearmanr(M.frac_top, M.ijsem_anaerobe); p1 = p2 / 2 if rho > 0 else 1 - p2 / 2
    A = M.dropna(subset=["mean_ra"]); X = sm.add_constant(np.column_stack([A.ijsem_anaerobe, np.log10(A.mean_ra + 1e-6)]))
    r = sm.OLS(A.frac_top.values, X).fit(cov_type="HC3")
    agree = M.dropna(subset=["anaerobe"]); cm = float(np.mean((agree.ijsem_anaerobe >= 0.5) == (agree.anaerobe >= 0.5)))
    out = {"n_genera": len(M), "spearman_rho": float(rho), "p_one_sided": float(p1), "ols_adj_abundance": {"n": len(A), "slope_anaerobe": float(r.params[1]), "p_two_sided_HC3": float(r.pvalues[1]), "slope_log_abund": float(r.params[2])},
           "agreement_with_madin_binary": {"n": len(agree), "frac_agree": cm}, "verdict": "PASS" if (p1 < 0.05 and r.params[1] > 0) else "FAIL"}
    M.to_csv("results/keystone_ijsem_genus.csv", index=False); json.dump(out, open("results/keystone_ijsem.json", "w"), indent=1); print(json.dumps(out, indent=1))
