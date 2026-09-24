"""Genomic check of the anaerobe-keystone candidate with KEGG (rest.kegg.jp: list/genome, link/genes/<KO>).
Per KEGG genome, presence of marker KOs; per genus (first word of the organism name), fraction of genomes carrying each module:
  anaerobic: PFOR (K00169 porA or K03737 nifJ), [FeFe]-hydrogenase (K00532/K00533), dissimilatory sulfate reduction (K11180 dsrA & K11181 dsrB & K00394 aprA)
  aerobic: cytochrome c oxidase aa3 (K02274 coxA), catalase (K03781 katE), cytochrome bd (K00425 cydA - microaerobic/aerotolerant)
Genomic anaerobe index GAI = PFOR - coxA (genus fractions). Tests: agreement with Madin anaerobe share; Spearman with frac_top;
within-study FE logit top ~ GAI + log abundance + prevalence (same design as keystone_traits_abundance.py).
Outputs: results/keystone_kegg_genus.csv, results/keystone_kegg.json"""
import re, json, numpy as np, pandas as pd, statsmodels.formula.api as smf
from scipy.stats import spearmanr
G = pd.read_csv("data/kegg/genome.tsv", sep="\t", header=None, names=["tid", "desc"])
G = G[G.desc.str.contains(";")]; G["org"] = G.desc.str.split(";").str[0].str.split(",").str[0].str.strip()
G["name"] = G.desc.str.split(";", n=1).str[1].str.strip().str.replace(r"^(Candidatus|\[?)\s*", "", regex=True).str.replace(r"[\[\]]", "", regex=True)
G["genus"] = G.name.str.split().str[0]
def orgs(k): return set(pd.read_csv(f"data/kegg/{k}.tsv", sep="\t", header=None)[1].str.split(":").str[0])
KO = {k: orgs(k) for k in ["K11180", "K11181", "K00394", "K00169", "K03737", "K00532", "K00533", "K02274", "K03781", "K00425"]}
G["PFOR"] = G.org.isin(KO["K00169"] | KO["K03737"]); G["FeFe_H2ase"] = G.org.isin(KO["K00532"] | KO["K00533"])
G["DSR"] = G.org.isin(KO["K11180"] & KO["K11181"] & KO["K00394"]); G["coxA"] = G.org.isin(KO["K02274"]); G["katE"] = G.org.isin(KO["K03781"]); G["cydA"] = G.org.isin(KO["K00425"])
M = ["PFOR", "FeFe_H2ase", "DSR", "coxA", "katE", "cydA"]
gen = G.groupby("genus")[M].mean(); gen["n_genomes"] = G.groupby("genus").size(); gen["GAI"] = gen.PFOR - gen.coxA
K = pd.read_csv("results/keystone_traits.csv")[["genus", "genus_clean", "frac_top", "p", "anaerobe"]].merge(gen, left_on="genus_clean", right_index=True, how="left")
K.to_csv("results/keystone_kegg_genus.csv", index=False)
out = {"n_kegg_genomes": len(G), "n_genera_mapped": int(K.n_genomes.notna().sum()), "n_genera": len(K), "vs_madin_anaerobe": {}, "vs_frac_top": {}}
for c in M + ["GAI"]:
    s = K.dropna(subset=[c, "anaerobe"]); out["vs_madin_anaerobe"][c] = list(spearmanr(s[c], s.anaerobe))
    s = K.dropna(subset=[c]); out["vs_frac_top"][c] = list(spearmanr(s[c], s.frac_top)) + [len(s)]
P = pd.read_csv("results/keystone_per_study.csv.gz").merge(pd.read_csv("results/keystone_genus_abundance.csv.gz"), on=["study", "genus"])
D = P.merge(gen[["GAI", "PFOR", "coxA", "DSR"]], left_on="genus", right_index=True).dropna(subset=["GAI"])
D["lra"] = np.log10(D.mean_ra + 1e-6); D["top"] = D.top.astype(int); D = D[D.groupby("study").top.transform("sum") > 0]
for name, f in [("GAI", "top ~ GAI + lra + prevalence + C(study)"), ("PFOR_coxA", "top ~ PFOR + coxA + lra + prevalence + C(study)"), ("DSR", "top ~ DSR + lra + prevalence + C(study)")]:
    m = smf.logit(f, D).fit(disp=0, cov_type="cluster", cov_kwds={"groups": pd.factorize(D.study)[0]}, maxiter=200)
    keep = [k for k in m.params.index if not k.startswith("C(")]; out[f"fe_logit_{name}"] = {"coef": m.params[keep].to_dict(), "p": m.pvalues[keep].to_dict(), "n_rows": len(D), "n_studies": int(D.study.nunique())}
json.dump(out, open("results/keystone_kegg.json", "w"), indent=1, default=float); print(json.dumps(out, indent=1, default=float))
