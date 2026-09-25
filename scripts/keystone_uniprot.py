"""Pre-registered (results/preregistration_uniprot.md) UniProt anaerobe-index replication."""
import json, os, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
import numpy as np, pandas as pd, statsmodels.api as sm
from scipy.stats import spearmanr

API = "https://rest.uniprot.org/uniprotkb/search?size=0&query="
Q = {"n_cox": "ec:7.1.1.9", "n_pfor": "ec:1.2.7.1", "n_recA": "gene_exact:recA"}


def total(q):
    for k in range(3):
        try:
            with urllib.request.urlopen(API + urllib.parse.quote(q), timeout=40) as r:
                return int(r.headers["X-Total-Results"])
        except Exception:
            time.sleep(1 + k)
    return None


def one(row):
    g, tid = row
    return {"genus_clean": g, **{k: total(f"taxonomy_id:{int(tid)} AND {v} AND keyword:KW-1185") for k, v in Q.items()}}


def ugai(d):
    ok = d.n_recA >= 1
    return np.where(ok, np.minimum(1, d.n_pfor / d.n_recA.clip(lower=1)) - np.minimum(1, d.n_cox / d.n_recA.clip(lower=1)), np.nan)


def main(out="results/keystone_uniprot.json", cache="results/keystone_uniprot_counts.csv"):
    E = pd.read_csv("results/keystone_ena_counts.csv").dropna(subset=["ena_taxid"])
    if not os.path.exists(cache):
        with ThreadPoolExecutor(8) as ex: res = list(ex.map(one, zip(E.genus_clean, E.ena_taxid)))
        pd.DataFrame(res).to_csv(cache, index=False)
    C = pd.read_csv(cache); C["UGAI"] = ugai(C)
    K = pd.read_csv("results/keystone_kegg_genus.csv").drop_duplicates("genus_clean")
    ab = pd.read_csv("results/keystone_genus_abundance.csv.gz").groupby("genus").mean_ra.mean().rename("mean_ra")
    M = K.merge(C, on="genus_clean").merge(ab, left_on="genus_clean", right_index=True, how="left").dropna(subset=["UGAI"])
    v = M.dropna(subset=["GAI"]); rv = float(spearmanr(v.UGAI, v.GAI)[0])
    A = M.dropna(subset=["mean_ra"]); r = sm.OLS(A.frac_top.values, sm.add_constant(np.column_stack([A.UGAI, np.log10(A.mean_ra + 1e-6)]))).fit(cov_type="HC3")
    J = {"tool": "UniProt REST (uniprotkb search counts, reference proteomes)", "n_queried": int(len(C)), "n_with_recA": int(len(M)),
         "spearman_UGAI_vs_KEGG_GAI": rv, "n_validation": int(len(v)), "G1_pass": bool(len(M) >= 150 and rv >= 0.6),
         "spearman_frac_top_vs_UGAI": [float(x) for x in spearmanr(M.frac_top, M.UGAI)],
         "ols": {"n": int(len(A)), "slope_UGAI": float(r.params[1]), "p_HC3": float(r.pvalues[1])}}
    J["U1_pass"] = bool(J["G1_pass"] and J["ols"]["slope_UGAI"] > 0 and J["ols"]["p_HC3"] < 0.05)
    json.dump(J, open(out, "w"), indent=1); print(json.dumps(J))


if __name__ == "__main__":
    main(*sys.argv[1:])
