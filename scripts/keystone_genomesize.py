"""Pre-registered (results/preregistration_genomesize.md) genome-streamlining rival test.
Genome stats: NCBI Datasets v2 API /genome/taxon/<genus>/dataset_report?filters.reference_only=true&page_size=20, cached in data/ncbi_datasets/."""
import json, glob, os, numpy as np, pandas as pd, statsmodels.api as sm

def genus_stats(report):
    L = [float(r["assembly_stats"]["total_sequence_length"]) / 1e6 for r in report.get("reports", []) if "total_sequence_length" in r.get("assembly_stats", {})]
    G = [float(r["assembly_stats"]["gc_percent"]) for r in report.get("reports", []) if "gc_percent" in r.get("assembly_stats", {})]
    return (np.median(L) if L else np.nan, np.median(G) if G else np.nan, len(L))

if __name__ == "__main__":
    rows = []
    for f in glob.glob("data/ncbi_datasets/*.json"):
        try: rep = json.load(open(f))
        except Exception: continue
        L, G, n = genus_stats(rep); rows.append({"genus_clean": os.path.basename(f)[:-5], "genome_mb": L, "gc": G, "n_ref_genomes": n})
    S = pd.DataFrame(rows).dropna()
    K = pd.read_csv("results/keystone_kegg_genus.csv").drop_duplicates("genus_clean")
    ab = pd.read_csv("results/keystone_genus_abundance.csv.gz").groupby("genus").mean_ra.mean().rename("mean_ra")
    M = K.merge(S, on="genus_clean").merge(ab, left_on="genus_clean", right_index=True, how="left").dropna(subset=["GAI", "mean_ra"])
    M["log_mb"] = np.log10(M.genome_mb); M["log_ab"] = np.log10(M.mean_ra + 1e-6)
    def fit(cols):
        r = sm.OLS(M.frac_top, sm.add_constant(M[cols])).fit(cov_type="HC3")
        return {c: {"slope": float(r.params[c]), "p": float(r.pvalues[c])} for c in cols} | {"r2": float(r.rsquared)}
    out = {"n_genera": len(M), "genomes_used": int(M.n_ref_genomes.sum()),
           "size_only": fit(["log_mb", "gc", "log_ab"]), "full": fit(["GAI", "log_mb", "gc", "log_ab"]),
           "corr_GAI_logmb": float(M[["GAI", "log_mb"]].corr(method="spearman").iloc[0, 1])}
    f = out["full"]; out["verdict_anaerobe"] = "PASS" if f["GAI"]["slope"] > 0 and f["GAI"]["p"] < 0.05 else "FAIL"
    out["rival_R_supported"] = bool(f["log_mb"]["p"] < 0.05 and f["GAI"]["p"] >= 0.05)
    M.to_csv("results/keystone_genomesize_genus.csv", index=False); json.dump(out, open("results/keystone_genomesize.json", "w"), indent=1); print(json.dumps(out, indent=1))
