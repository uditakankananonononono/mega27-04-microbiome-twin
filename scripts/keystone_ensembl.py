"""Pre-registered (results/preregistration_ensembl.md) sequencing-effort control with Ensembl Genomes via EBI Search."""
import json, os, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
import numpy as np, pandas as pd, statsmodels.api as sm
from scipy.stats import spearmanr

API = "https://www.ebi.ac.uk/ebisearch/ws/rest/ensemblGenomes_genome?size=0&format=json&query="


def hits(genus):
    for k in range(3):
        try:
            return int(json.load(urllib.request.urlopen(API + urllib.parse.quote(genus), timeout=40))["hitCount"])
        except Exception:
            time.sleep(1 + k)
    return None


def main(out="results/keystone_ensembl.json", cache="results/keystone_ensembl_counts.csv"):
    K = pd.read_csv("results/keystone_kegg_genus.csv").dropna(subset=["GAI"]).drop_duplicates("genus_clean")
    if not os.path.exists(cache):
        with ThreadPoolExecutor(2) as ex: w = list(ex.map(hits, K.genus_clean))
        pd.DataFrame({"genus_clean": K.genus_clean, "ensembl_genomes": w}).to_csv(cache, index=False)
    C = pd.read_csv(cache); E = pd.read_csv("results/keystone_ena_counts.csv")
    ab = pd.read_csv("results/keystone_genus_abundance.csv.gz").groupby("genus").mean_ra.mean().rename("mean_ra")
    M = K.merge(C, on="genus_clean").merge(ab, left_on="genus_clean", right_index=True, how="left").dropna(subset=["ensembl_genomes", "mean_ra"])
    X = sm.add_constant(np.column_stack([M.GAI, np.log10(1 + M.ensembl_genomes), np.log10(M.mean_ra + 1e-6)]))
    r = sm.OLS(M.frac_top.values, X).fit(cov_type="HC3")
    ME = M.merge(E, on="genus_clean").dropna(subset=["ena_assemblies"])
    J = {"tool": "EBI Search REST (Ensembl Genomes genome domain)", "n_genera": int(len(K)), "n_with_counts": int(C.ensembl_genomes.notna().sum()), "n_model": int(len(M)),
         "G1_pass": bool(C.ensembl_genomes.notna().sum() >= 180),
         "slope_GAI": float(r.params[1]), "p_GAI_HC3": float(r.pvalues[1]), "slope_log_genomes": float(r.params[2]), "p_log_genomes": float(r.pvalues[2]),
         "spearman_ensembl_vs_ena": [float(x) for x in spearmanr(ME.ensembl_genomes, ME.ena_assemblies)]}
    J["S1_pass"] = bool(J["G1_pass"] and J["slope_GAI"] > 0 and J["p_GAI_HC3"] < 0.05)
    json.dump(J, open(out, "w"), indent=1); print(json.dumps(J))


if __name__ == "__main__":
    main(*sys.argv[1:])
