"""Pre-registered (results/preregistration_pubtator.md): literature oral index via PubTator3."""
import json, os, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
import numpy as np, pandas as pd, statsmodels.formula.api as smf
from scipy.stats import spearmanr
sys.path.insert(0, "scripts")
import keystone_methodgeneral as mg

API = "https://www.ncbi.nlm.nih.gov/research/pubtator3-api/search/?text="
CACHE = "results/keystone_pubtator_counts.csv"


def count(text):
    for k in range(3):
        try:
            return int(json.load(urllib.request.urlopen(API + urllib.parse.quote(text), timeout=40))["count"])
        except Exception:
            time.sleep(1 + k)
    return None


def fill(budget):
    K = pd.read_csv("results/keystone_kegg_genus.csv").dropna(subset=["GAI"]).drop_duplicates("genus_clean")
    C = pd.read_csv(CACHE) if os.path.exists(CACHE) else pd.DataFrame({"genus_clean": K.genus_clean, "n_all": np.nan, "n_oral": np.nan})
    t0 = time.time()
    while time.time() - t0 < budget:
        todo = [(i, c) for i in C.index for c in ["n_all", "n_oral"] if pd.isna(C.at[i, c])][:10]
        if not todo: break
        q = lambda x: C.at[x[0], "genus_clean"] if x[1] == "n_all" else f"{C.at[x[0], 'genus_clean']} AND (oral OR dental)"
        with ThreadPoolExecutor(2) as ex: vals = list(ex.map(lambda x: count(q(x)), todo))
        for (i, c), v in zip(todo, vals): C.at[i, c] = v if v is not None else np.nan
        C.to_csv(CACHE, index=False)
    return C


def fit(L, CNT):
    A = pd.read_csv("results/keystone_genus_abundance.csv.gz")
    K = pd.read_csv("results/keystone_kegg_genus.csv")[["genus", "genus_clean", "GAI"]].dropna().drop_duplicates("genus")
    D = L.merge(A, on=["study", "genus"]).merge(K, on="genus").merge(CNT[["genus_clean", "OLF_z"]], on="genus_clean").dropna(subset=["OLF_z"])
    D["lra"] = np.log10(D.mean_ra + 1e-6); D = D[D.groupby("study").top.transform("sum") > 0]
    m = smf.logit("top ~ OLF_z + GAI + lra + prevalence + C(study)", D).fit(disp=0, cov_type="cluster", cov_kwds={"groups": pd.factorize(D.study)[0]}, maxiter=300)
    return {"n_rows": int(len(D)), "coef_OLF_z": float(m.params["OLF_z"]), "p_OLF_z": float(m.pvalues["OLF_z"]), "converged": bool(m.mle_retvals["converged"])}


def main(budget=90):
    C = fill(float(budget)); miss = int(C[["n_all", "n_oral"]].isna().sum().sum()); print("missing", miss)
    if miss: return
    C["OLF"] = np.where(C.n_all >= 5, C.n_oral / C.n_all.clip(lower=1), np.nan); C["OLF_z"] = (C.OLF - C.OLF.mean()) / C.OLF.std()
    R = pd.read_csv("results/keystone_per_study.csv.gz")[["study", "genus", "top"]]; R["top"] = mg.truthy(R.top)
    out = {}
    for k, f in [("gglasso", "results/keystone_gglasso_per_study.csv.gz"), ("igraph", "results/keystone_igraph_per_study.csv.gz")]:
        L = pd.read_csv(f).dropna(subset=["genus"]); out[k] = fit(L.assign(top=mg.truthy(L.top_gl))[["study", "genus", "top"]], C)
    out["ridge_reported_only"] = fit(R, C)
    v = C.dropna(subset=["OLF"])
    J = {"tool": "NCBI PubTator3 API (search counts)", "n_genera": int(len(C)), "n_with_OLF": int(len(v)), "G1_pass": bool(len(v) >= 180),
         "spearman_OLF_vs_HOMD_oral": [float(x) for x in spearmanr(v.OLF, v.genus_clean.isin(mg.ORAL))], **out}
    J["PT1_pass"] = bool(J["G1_pass"] and all(J[k]["coef_OLF_z"] > 0 and J[k]["p_OLF_z"] < 0.05 for k in ["gglasso", "igraph"]))
    json.dump(J, open("results/keystone_pubtator.json", "w"), indent=1); print(json.dumps(J))


if __name__ == "__main__":
    main(*sys.argv[1:])
