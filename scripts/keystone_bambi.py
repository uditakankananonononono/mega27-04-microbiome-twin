"""Pre-registered (results/preregistration_bambi.md): Bayesian hierarchical oral effect."""
import json, sys
import numpy as np, pandas as pd
sys.path.insert(0, "scripts")
import keystone_methodgeneral as mg


def rows(L):
    A = pd.read_csv("results/keystone_genus_abundance.csv.gz")
    K = pd.read_csv("results/keystone_kegg_genus.csv")[["genus", "genus_clean", "GAI"]].dropna().drop_duplicates("genus")
    D = L.merge(A, on=["study", "genus"]).merge(K, on="genus")
    D["oral"] = D.genus_clean.isin(mg.ORAL).astype(int); D["lra"] = np.log10(D.mean_ra + 1e-6)
    return D[D.groupby("study").top.transform("sum") > 0].reset_index(drop=True)


def fit(D):
    import bambi as bmb, arviz as az
    m = bmb.Model("top ~ oral + GAI + lra + prevalence + (1|study)", D[["top", "oral", "GAI", "lra", "prevalence", "study"]], family="bernoulli")
    idata = m.fit(draws=500, tune=500, chains=2, random_seed=0, progressbar=False)
    post = idata.posterior; o = post["oral"].values.ravel(); g = post["GAI"].values.ravel()
    rh = float(az.rhat(idata, var_names=["oral", "GAI", "lra", "prevalence"]).to_array().max())
    hdi = lambda x: [float(v) for v in az.hdi(x, hdi_prob=0.95)]
    return {"n_rows": int(len(D)), "oral_mean": float(o.mean()), "oral_hdi95": hdi(o), "P_oral_gt0": float((o > 0).mean()),
            "GAI_mean": float(g.mean()), "GAI_hdi95": hdi(g), "max_rhat": rh}


def main(which):
    f = {"gglasso": "results/keystone_gglasso_per_study.csv.gz", "igraph": "results/keystone_igraph_per_study.csv.gz"}[which]
    L = pd.read_csv(f).dropna(subset=["genus"]); L = L.assign(top=mg.truthy(L.top_gl))[["study", "genus", "top"]]
    json.dump(fit(rows(L)), open(f"/tmp/bambi_{which}.json", "w"))


def combine():
    J = {k: json.load(open(f"/tmp/bambi_{k}.json")) for k in ["gglasso", "igraph"]}
    J["tool"] = "bambi / PyMC (Bayesian hierarchical logistic)"
    J["BY1_pass"] = bool(all(J[k]["P_oral_gt0"] >= 0.975 for k in ["gglasso", "igraph"]))
    json.dump(J, open("results/keystone_bambi.json", "w"), indent=1); print(json.dumps(J))


if __name__ == "__main__":
    combine() if sys.argv[1] == "combine" else main(sys.argv[1])
