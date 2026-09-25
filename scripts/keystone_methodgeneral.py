"""Pre-registered (results/preregistration_methodgeneral.md): method-general keystone correlates."""
import json, sys
import numpy as np, pandas as pd, statsmodels.formula.api as smf
sys.path.insert(0, "scripts")
from keystone_homd import oral_genera

T = pd.read_csv("data/ref/HOMD_taxon_table_v4.2.csv", sep="\t", skiprows=1, dtype=str)
ORAL, _, _ = oral_genera(T)


def truthy(s):
    return s.astype(str).str.lower().isin(["true", "1", "1.0"]).astype(int)


def fit(L):
    A = pd.read_csv("results/keystone_genus_abundance.csv.gz")
    K = pd.read_csv("results/keystone_kegg_genus.csv")[["genus", "genus_clean", "GAI"]].dropna().drop_duplicates("genus")
    D = L.merge(A, on=["study", "genus"]).merge(K, on="genus")
    D["oral"] = D.genus_clean.isin(ORAL).astype(int); D["lra"] = np.log10(D.mean_ra + 1e-6)
    D = D[D.groupby("study").top.transform("sum") > 0]
    m = smf.logit("top ~ oral + GAI + lra + prevalence + C(study)", D).fit(disp=0, cov_type="cluster", cov_kwds={"groups": pd.factorize(D.study)[0]}, maxiter=300)
    return {"n_rows": int(len(D)), "n_studies": int(D.study.nunique()), "n_oral_rows": int(D.oral.sum()),
            "coef_oral": float(m.params["oral"]), "p_oral": float(m.pvalues["oral"]), "coef_GAI": float(m.params["GAI"]), "p_GAI": float(m.pvalues["GAI"])}


def main():
    R = pd.read_csv("results/keystone_per_study.csv.gz")[["study", "genus", "top"]]; R["top"] = truthy(R.top)
    G = pd.read_csv("results/keystone_gglasso_per_study.csv.gz").dropna(subset=["genus"]); G = G.assign(top=truthy(G.top_gl))[["study", "genus", "top"]]
    I = pd.read_csv("results/keystone_igraph_per_study.csv.gz").dropna(subset=["genus"]); I = I.assign(top=truthy(I.top_gl))[["study", "genus", "top"]]
    J = {"ridge_reported_only": fit(R), "gglasso": fit(G), "igraph": fit(I)}
    J["MG1_pass"] = bool(all(J[k]["coef_oral"] > 0 and J[k]["p_oral"] < 0.05 for k in ["gglasso", "igraph"]))
    json.dump(J, open("results/keystone_methodgeneral.json", "w"), indent=1); print(json.dumps(J))


if __name__ == "__main__":
    main()
