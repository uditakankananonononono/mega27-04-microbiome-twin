"""Pre-registered (results/preregistration_homd.md): oral-taxon rival via HOMD."""
import json, os, urllib.request
import numpy as np, pandas as pd, statsmodels.api as sm

URL = "https://www.homd.org/ftp/taxonomy/HOMD_taxon_table_v4.2.csv"; LOCAL = "data/ref/HOMD_taxon_table_v4.2.csv"


def oral_genera(T):
    gcol = next(c for c in T.columns if "genus" in c.lower())
    scol = next((c for c in T.columns if "site" in c.lower()), None)
    if scol is not None: T = T[T[scol].astype(str).str.contains("oral", case=False)]
    return set(T[gcol].astype(str).str.strip()), gcol, scol


def ols(M):
    r = sm.OLS(M.frac_top.values, sm.add_constant(np.column_stack([M.GAI, M.oral, np.log10(M.mean_ra + 1e-6)]))).fit(cov_type="HC3"); return r


def main():
    if not os.path.exists(LOCAL):
        os.makedirs("data/ref", exist_ok=True); urllib.request.urlretrieve(URL, LOCAL)
    T = pd.read_csv(LOCAL, sep="\t", skiprows=1, dtype=str); og, gcol, scol = oral_genera(T)
    K = pd.read_csv("results/keystone_kegg_genus.csv").dropna(subset=["GAI"]).drop_duplicates("genus_clean")
    ab = pd.read_csv("results/keystone_genus_abundance.csv.gz").groupby("genus").mean_ra.mean().rename("mean_ra")
    M = K.merge(ab, left_on="genus_clean", right_index=True).dropna(subset=["mean_ra"]).copy(); M["oral"] = M.genus_clean.isin(og).astype(int)
    r = ols(M); N = M[M.oral == 0]
    rn = sm.OLS(N.frac_top.values, sm.add_constant(np.column_stack([N.GAI, np.log10(N.mean_ra + 1e-6)]))).fit(cov_type="HC3")
    J = {"tool": "HOMD taxon table v4.2", "genus_column": gcol, "site_column": scol, "n_homd_genera": len(og), "n_model": int(len(M)), "n_oral": int(M.oral.sum()),
         "G1_pass": bool(M.oral.sum() >= 20), "slope_GAI": float(r.params[1]), "p_GAI_HC3": float(r.pvalues[1]),
         "coef_oral": float(r.params[2]), "p_oral": float(r.pvalues[2]), "nonoral": {"n": int(len(N)), "slope_GAI": float(rn.params[1]), "p_HC3": float(rn.pvalues[1])},
         "oral_top10_frac_top": M.sort_values("frac_top", ascending=False).head(10)[["genus_clean", "oral"]].values.tolist()}
    J["M1_pass"] = bool(J["G1_pass"] and J["slope_GAI"] > 0 and J["p_GAI_HC3"] < 0.05)
    json.dump(J, open("results/keystone_homd.json", "w"), indent=1); print(json.dumps(J))


if __name__ == "__main__":
    main()
