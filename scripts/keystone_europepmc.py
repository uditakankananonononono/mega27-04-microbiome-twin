"""Pre-registered (results/preregistration_europepmc.md) study-bias control for the Disbiome keystone-literature link."""
import json, os, sys, time, urllib.parse, urllib.request
import numpy as np, pandas as pd, statsmodels.api as sm
from scipy.stats import spearmanr

API = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&pageSize=1&resultType=idlist&query="


def hits(genus):
    q = urllib.parse.quote(f'TITLE_ABS:"{genus}"')
    for k in range(3):
        try:
            return int(json.load(urllib.request.urlopen(API + q, timeout=30))["hitCount"])
        except Exception:
            time.sleep(1 + k)
    return None


def main(out="results/keystone_europepmc.json", cache="results/keystone_europepmc_counts.csv"):
    D = pd.read_csv("results/keystone_disbiome_genus.csv")
    if os.path.exists(cache):
        C = pd.read_csv(cache)
    else:
        C = pd.DataFrame({"genus_clean": D.genus_clean, "epmc_hits": [hits(g) for g in D.genus_clean]}); C.to_csv(cache, index=False)
    M = D.merge(C, on="genus_clean"); ok = M.dropna(subset=["epmc_hits"])
    X = sm.add_constant(pd.DataFrame({"kscore": ok.kscore, "log_studies": np.log(ok.studies), "log_epmc": np.log1p(ok.epmc_hits)}))
    r = sm.NegativeBinomial(ok.n_exp, X).fit(disp=0)
    J = {"tool": "Europe PMC REST API (search hitCount)", "n_genera": int(len(M)), "n_with_hits": int(len(ok)), "G1_pass": bool(len(ok) >= 240),
         "spearman_kscore_vs_log_hits": [float(x) for x in spearmanr(ok.kscore, np.log1p(ok.epmc_hits))],
         "nb_ml": {"alpha": float(r.params["alpha"]), "coef_kscore": float(r.params["kscore"]), "p_kscore": float(r.pvalues["kscore"]),
                   "coef_log_epmc": float(r.params["log_epmc"]), "p_log_epmc": float(r.pvalues["log_epmc"])}}
    J["E1_pass"] = bool(J["G1_pass"] and J["nb_ml"]["coef_kscore"] > 0 and J["nb_ml"]["p_kscore"] < 0.05)
    json.dump(J, open(out, "w"), indent=1); print(json.dumps(J))


if __name__ == "__main__":
    main(*sys.argv[1:])
