"""Pre-registered (results/preregistration_openalex.md) OpenAlex literature-volume control."""
import json, os, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
import numpy as np, pandas as pd, statsmodels.api as sm

API = "https://api.openalex.org/works?per_page=1&filter="


def works(genus):
    for k in range(3):
        try:
            return int(json.load(urllib.request.urlopen(API + urllib.parse.quote(f"title_and_abstract.search:{genus}"), timeout=40))["meta"]["count"])
        except Exception:
            time.sleep(1 + k)
    return None


def nb(y, D):
    X = sm.add_constant(pd.DataFrame({"kscore": D.kscore, "log_studies": np.log(D.studies), "log_oa": np.log1p(D.oa_works)}))
    r = sm.NegativeBinomial(y, X).fit(disp=0)
    return {"alpha": float(r.params["alpha"]), "coef_kscore": float(r.params["kscore"]), "p_kscore": float(r.pvalues["kscore"]),
            "coef_log_oa": float(r.params["log_oa"]), "p_log_oa": float(r.pvalues["log_oa"])}


def main(out="results/keystone_openalex.json", cache="results/keystone_openalex_counts.csv"):
    D = pd.read_csv("results/keystone_disbiome_genus.csv")
    if not os.path.exists(cache):
        with ThreadPoolExecutor(6) as ex: w = list(ex.map(works, D.genus_clean))
        pd.DataFrame({"genus_clean": D.genus_clean, "oa_works": w}).to_csv(cache, index=False)
    C = pd.read_csv(cache); B = pd.read_csv("results/keystone_bugsigdb.csv")[["genus_clean", "bugsigdb_signatures"]]
    M = D.merge(C, on="genus_clean").merge(B, on="genus_clean", how="left").dropna(subset=["oa_works"])
    J = {"tool": "OpenAlex API (works count)", "n_genera": int(len(D)), "n_with_counts": int(len(M)), "G1_pass": bool(len(M) >= 240),
         "O1_disbiome": nb(M.n_exp, M), "O2_bugsigdb": nb(M.bugsigdb_signatures.fillna(0).astype(int), M)}
    J["O1_pass"] = bool(J["G1_pass"] and J["O1_disbiome"]["coef_kscore"] > 0 and J["O1_disbiome"]["p_kscore"] < 0.05)
    J["O2_pass"] = bool(J["G1_pass"] and J["O2_bugsigdb"]["coef_kscore"] > 0 and J["O2_bugsigdb"]["p_kscore"] < 0.05)
    json.dump(J, open(out, "w"), indent=1); print(json.dumps(J))


if __name__ == "__main__":
    main(*sys.argv[1:])
