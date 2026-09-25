"""Pre-registered (results/preregistration_interpro.md) InterPro anaerobe-index replication. Re-run with a time budget (argv[1] s) until complete."""
import json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
import numpy as np, pandas as pd, statsmodels.api as sm
from scipy.stats import spearmanr

API = "https://www.ebi.ac.uk/interpro/api/protein/uniprot/taxonomy/uniprot/{tid}/entry/interpro/{ipr}?page_size=1"
E = {"n_pfor": "IPR011895", "n_cox": "IPR000883", "n_recA": "IPR013765"}
CACHE = "results/keystone_interpro_counts.csv"


def count(tid, ipr):
    for k in range(3):
        try:
            with urllib.request.urlopen(API.format(tid=int(tid), ipr=ipr), timeout=60) as r:
                if r.status == 204: return 0
                b = r.read()
                return 0 if not b.strip() else int(json.loads(b)["count"])
        except Exception:
            time.sleep(1 + k)
    return None


def igai(d):
    ok = d.n_recA >= 1
    return np.where(ok, np.minimum(1, d.n_pfor / d.n_recA.clip(lower=1)) - np.minimum(1, d.n_cox / d.n_recA.clip(lower=1)), np.nan)


def fill(budget):
    G = pd.read_csv("results/keystone_ena_counts.csv").dropna(subset=["ena_taxid"])[["genus_clean", "ena_taxid"]]
    C = pd.read_csv(CACHE) if os.path.exists(CACHE) else G.assign(**{k: np.nan for k in E})
    t0 = time.time()
    while time.time() - t0 < budget:
        todo = [(i, k) for i in C.index for k in E if pd.isna(C.at[i, k])][:12]
        if not todo: break
        with ThreadPoolExecutor(3) as ex: vals = list(ex.map(lambda x: count(C.at[x[0], "ena_taxid"], E[x[1]]), todo))
        for (i, k), v in zip(todo, vals): C.at[i, k] = v if v is not None else np.nan
        C.to_csv(CACHE, index=False)
    return C


def main(budget=90):
    C = fill(float(budget)); miss = int(C[list(E)].isna().sum().sum()); print("missing cells", miss)
    if miss: return
    C["IGAI"] = igai(C)
    K = pd.read_csv("results/keystone_kegg_genus.csv").drop_duplicates("genus_clean")
    ab = pd.read_csv("results/keystone_genus_abundance.csv.gz").groupby("genus").mean_ra.mean().rename("mean_ra")
    M = K.merge(C, on="genus_clean").merge(ab, left_on="genus_clean", right_index=True, how="left").dropna(subset=["IGAI"])
    v = M.dropna(subset=["GAI"]); rv = float(spearmanr(v.IGAI, v.GAI)[0])
    A = M.dropna(subset=["mean_ra"]); r = sm.OLS(A.frac_top.values, sm.add_constant(np.column_stack([A.IGAI, np.log10(A.mean_ra + 1e-6)]))).fit(cov_type="HC3")
    J = {"tool": "InterPro API (protein counts per taxon and entry)", "n_queried": int(len(C)), "n_with_recA": int(len(M)),
         "spearman_IGAI_vs_KEGG_GAI": rv, "n_validation": int(len(v)), "G1_pass": bool(len(M) >= 150 and rv >= 0.6),
         "spearman_frac_top_vs_IGAI": [float(x) for x in spearmanr(M.frac_top, M.IGAI)],
         "ols": {"n": int(len(A)), "slope_IGAI": float(r.params[1]), "p_HC3": float(r.pvalues[1])}}
    J["P1_pass"] = bool(J["G1_pass"] and J["ols"]["slope_IGAI"] > 0 and J["ols"]["p_HC3"] < 0.05)
    json.dump(J, open("results/keystone_interpro.json", "w"), indent=1); print(json.dumps(J))


if __name__ == "__main__":
    main(*sys.argv[1:])
