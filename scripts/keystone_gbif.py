"""Pre-registered (results/preregistration_gbif.md) generalism rival with the GBIF API."""
import json, os, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
import numpy as np, pandas as pd, statsmodels.api as sm

API = "https://api.gbif.org/v1"


def getj(url):
    for k in range(3):
        try:
            return json.load(urllib.request.urlopen(url, timeout=40))
        except Exception:
            time.sleep(1 + k)
    return None


def accept(m):
    return bool(m) and m.get("matchType") == "EXACT" and m.get("rank") == "GENUS" and m.get("kingdom") in ("Bacteria", "Archaea")


def one(genus):
    m = getj(f"{API}/species/match?" + urllib.parse.urlencode({"name": genus, "rank": "GENUS", "kingdom": "Bacteria"}))
    if not accept(m): return genus, None, None, None
    o = getj(f"{API}/occurrence/search?taxonKey={m['usageKey']}&limit=0&facet=country&facetLimit=300")
    if not o: return genus, m["usageKey"], None, None
    nc = sum(len(f["counts"]) for f in o.get("facets", []) if f["field"] == "COUNTRY")
    return genus, m["usageKey"], int(o["count"]), nc


def main(out="results/keystone_gbif.json", cache="results/keystone_gbif_counts.csv"):
    K = pd.read_csv("results/keystone_kegg_genus.csv").dropna(subset=["GAI"]).drop_duplicates("genus_clean")
    if not os.path.exists(cache):
        with ThreadPoolExecutor(8) as ex: res = list(ex.map(one, K.genus_clean))
        pd.DataFrame(res, columns=["genus_clean", "gbif_key", "occurrences", "countries"]).to_csv(cache, index=False)
    C = pd.read_csv(cache)
    ab = pd.read_csv("results/keystone_genus_abundance.csv.gz").groupby("genus").mean_ra.mean().rename("mean_ra")
    M = K.merge(C, on="genus_clean").merge(ab, left_on="genus_clean", right_index=True, how="left")
    M = M[(M.occurrences >= 1)].dropna(subset=["mean_ra"])
    X = sm.add_constant(np.column_stack([M.GAI, np.log10(1 + M.occurrences), np.log10(1 + M.countries), np.log10(M.mean_ra + 1e-6)]))
    r = sm.OLS(M.frac_top.values, X).fit(cov_type="HC3")
    J = {"tool": "GBIF API v1 (species/match + occurrence facets)", "n_genera": int(len(K)), "n_matched": int(C.gbif_key.notna().sum()), "n_model": int(len(M)),
         "G1_pass": bool(len(M) >= 150), "slope_GAI": float(r.params[1]), "p_GAI": float(r.pvalues[1]),
         "slope_log_occ": float(r.params[2]), "p_log_occ": float(r.pvalues[2]), "slope_log_countries": float(r.params[3]), "p_log_countries": float(r.pvalues[3])}
    J["B1_pass"] = bool(J["G1_pass"] and J["slope_GAI"] > 0 and J["p_GAI"] < 0.05)
    J["rival_G_supported"] = bool(((J["slope_log_occ"] > 0 and J["p_log_occ"] < 0.05) or (J["slope_log_countries"] > 0 and J["p_log_countries"] < 0.05)) and J["p_GAI"] >= 0.05)
    json.dump(J, open(out, "w"), indent=1); print(json.dumps(J))


if __name__ == "__main__":
    main(*sys.argv[1:])
