"""Pre-registered (results/preregistration_ena.md) sequencing-effort control with the ENA portal API."""
import json, os, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
import numpy as np, pandas as pd, statsmodels.api as sm
from scipy.stats import spearmanr

TAX = "https://www.ebi.ac.uk/ena/taxonomy/rest/scientific-name/"
CNT = "https://www.ebi.ac.uk/ena/portal/api/count?result=assembly&query="


def get(url):
    for k in range(3):
        try:
            return urllib.request.urlopen(url, timeout=40).read().decode()
        except Exception:
            time.sleep(1 + k)
    return None


def pick_taxid(recs):
    for r in recs or []:
        if r.get("rank") == "genus" and str(r.get("lineage", "")).startswith(("Bacteria", "Archaea")):
            return int(r["taxId"])
    return None


def parse_count(txt):
    if not txt: return None
    lines = [l for l in txt.strip().splitlines() if l.strip()]
    return int(lines[-1]) if len(lines) >= 2 and lines[-1].strip().isdigit() else None


def one(genus):
    t = get(TAX + urllib.parse.quote(genus)); tid = pick_taxid(json.loads(t)) if t and t.strip().startswith("[") else None
    c = parse_count(get(CNT + urllib.parse.quote(f"tax_tree({tid})"))) if tid else None
    return genus, tid, c


def main(out="results/keystone_ena.json", cache="results/keystone_ena_counts.csv"):
    K = pd.read_csv("results/keystone_kegg_genus.csv").dropna(subset=["GAI"]).drop_duplicates("genus_clean")
    if not os.path.exists(cache):
        with ThreadPoolExecutor(8) as ex: res = list(ex.map(one, K.genus_clean))
        pd.DataFrame(res, columns=["genus_clean", "ena_taxid", "ena_assemblies"]).to_csv(cache, index=False)
    C = pd.read_csv(cache)
    ab = pd.read_csv("results/keystone_genus_abundance.csv.gz").groupby("genus").mean_ra.mean().rename("mean_ra")
    M = K.merge(C, on="genus_clean").merge(ab, left_on="genus_clean", right_index=True, how="left").dropna(subset=["ena_assemblies", "mean_ra"])
    X = sm.add_constant(np.column_stack([M.GAI, np.log10(1 + M.ena_assemblies), np.log10(M.mean_ra + 1e-6)]))
    r = sm.OLS(M.frac_top.values, X).fit(cov_type="HC3")
    J = {"tool": "ENA portal API + ENA taxonomy REST", "n_genera": int(len(K)), "n_resolved": int(C.ena_assemblies.notna().sum()), "n_model": int(len(M)),
         "G1_pass": bool(C.ena_assemblies.notna().sum() >= 180),
         "slope_GAI": float(r.params[1]), "p_GAI_HC3": float(r.pvalues[1]), "slope_log_assemblies": float(r.params[2]), "p_log_assemblies": float(r.pvalues[2]),
         "spearman_assemblies_vs_kegg_genomes": [float(x) for x in spearmanr(M.ena_assemblies, M.n_genomes)],
         "spearman_frac_top_vs_log_assemblies": [float(x) for x in spearmanr(M.frac_top, np.log10(1 + M.ena_assemblies))]}
    J["A1_pass"] = bool(J["G1_pass"] and J["slope_GAI"] > 0 and J["p_GAI_HC3"] < 0.05)
    json.dump(J, open(out, "w"), indent=1); print(json.dumps(J))


if __name__ == "__main__":
    main(*sys.argv[1:])
