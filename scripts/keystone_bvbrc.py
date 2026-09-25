"""Third independent anaerobe source: BV-BRC genome metadata (www.bv-brc.org/api/genome, oxygen_requirement facet by genus;
Anaerobic / Aerobic / Facultative / Microaerophilic genome counts, fetched into data/bvbrc/bv_<class>.json).
Genus anaerobe share = anaerobic genomes / annotated genomes (genera with >= 3 annotated genomes).
Tests: agreement with Madin and KEGG GAI; Spearman with frac_top; within-study FE logit with abundance + prevalence.
Output: results/keystone_bvbrc.json, results/keystone_bvbrc_genus.csv"""
import json, numpy as np, pandas as pd, statsmodels.formula.api as smf
from scipy.stats import spearmanr
CNT = {}
for o in ["Anaerobic", "Aerobic", "Facultative", "Microaerophilic"]:
    f = json.load(open(f"data/bvbrc/bv_{o}.json"))["facet_counts"]["facet_fields"]["genus"]; CNT[o] = dict(zip(f[::2], f[1::2]))
B = pd.DataFrame(CNT).fillna(0); B["n_annot"] = B.sum(1); B = B[B.n_annot >= 3]; B["bv_anaerobe"] = B.Anaerobic / B.n_annot
K = pd.read_csv("results/keystone_kegg_genus.csv").merge(B[["bv_anaerobe", "n_annot"]], left_on="genus_clean", right_index=True, how="left")
K.to_csv("results/keystone_bvbrc_genus.csv", index=False)
s = K.dropna(subset=["bv_anaerobe"]); out = {"n_genera_bvbrc": len(s), "n_bvbrc_genomes_annotated": int(B.n_annot.sum()),
    "rho_vs_madin": list(spearmanr(s.dropna(subset=["anaerobe"]).bv_anaerobe, s.dropna(subset=["anaerobe"]).anaerobe)),
    "rho_vs_kegg_gai": list(spearmanr(s.dropna(subset=["GAI"]).bv_anaerobe, s.dropna(subset=["GAI"]).GAI)),
    "rho_vs_frac_top": list(spearmanr(s.bv_anaerobe, s.frac_top))}
P = pd.read_csv("results/keystone_per_study.csv.gz").merge(pd.read_csv("results/keystone_genus_abundance.csv.gz"), on=["study", "genus"])
D = P.merge(B[["bv_anaerobe"]], left_on="genus", right_index=True); D["lra"] = np.log10(D.mean_ra + 1e-6); D["top"] = D.top.astype(int)
D = D[D.groupby("study").top.transform("sum") > 0]
m = smf.logit("top ~ bv_anaerobe + lra + prevalence + C(study)", D).fit(disp=0, cov_type="cluster", cov_kwds={"groups": pd.factorize(D.study)[0]}, maxiter=200)
keep = [k for k in m.params.index if not k.startswith("C(")]
out["fe_logit"] = {"coef": m.params[keep].to_dict(), "p": m.pvalues[keep].to_dict(), "n_rows": len(D), "n_studies": int(D.study.nunique())}
json.dump(out, open("results/keystone_bvbrc.json", "w"), indent=1, default=float); print(json.dumps(out, indent=1, default=float))
