"""Pre-registered (results/preregistration_protraits.md) ProTraits check of anaerobe-keystone.
Source: http://protraits.irb.hr/data/ProTraits_binaryIntegratedPr0.95.txt (cached to data/protraits/, gitignored)."""
import json, os, sys, urllib.request
import numpy as np, pandas as pd, statsmodels.api as sm
from scipy.stats import spearmanr

URL = "http://protraits.irb.hr/data/ProTraits_binaryIntegratedPr0.95.txt"
COL = "oxygenreq=strictanaero"


def genus_share(df):
    d = df[["Organism_name", COL]].copy()
    d["an"] = pd.to_numeric(d[COL].astype(str).str.strip(), errors="coerce"); d = d[d.an.isin([0, 1])]
    nm = d.Organism_name.astype(str).str.strip(); d = d[~nm.str.startswith(("Candidatus", "["))]
    d["genus"] = d.Organism_name.astype(str).str.strip().str.split().str[0].str.capitalize()
    return d.groupby("genus").an.agg(["mean", "size"]).rename(columns={"mean": "pt_anaerobe", "size": "n_org"})


def main(out="results/keystone_protraits.json"):
    os.makedirs("data/protraits", exist_ok=True); f = "data/protraits/ProTraits_binaryIntegratedPr0.95.txt"
    if not os.path.exists(f):
        urllib.request.urlretrieve(URL, f)
    pt = genus_share(pd.read_csv(f, sep="\t", dtype=str, usecols=["Organism_name", COL]))
    K = pd.read_csv("results/keystone_kegg_genus.csv").drop_duplicates("genus_clean")
    ab = pd.read_csv("results/keystone_genus_abundance.csv.gz").groupby("genus").mean_ra.mean().rename("mean_ra")
    M = K.merge(pt, left_on="genus_clean", right_index=True).merge(ab, left_on="genus_clean", right_index=True, how="left")
    rho, p2 = spearmanr(M.frac_top, M.pt_anaerobe); p1 = p2 / 2 if rho > 0 else 1 - p2 / 2
    A = M.dropna(subset=["mean_ra"]); X = sm.add_constant(np.column_stack([A.pt_anaerobe, np.log10(A.mean_ra + 1e-6)]))
    r = sm.OLS(A.frac_top.values, X).fit(cov_type="HC3")
    g = M.dropna(subset=["GAI"]); ag = M.dropna(subset=["anaerobe"])
    J = {"tool": "ProTraits (protraits.irb.hr, integrated Pr>=0.95)", "n_genera": int(len(M)), "G1_pass": bool(len(M) >= 100),
         "spearman_rho": float(rho), "p_one_sided": float(p1),
         "ols_adj_abundance": {"n": int(len(A)), "slope": float(r.params[1]), "p_two_sided_HC3": float(r.pvalues[1])},
         "agreement": {"spearman_vs_GAI": float(spearmanr(g.pt_anaerobe, g.GAI)[0]), "n_gai": int(len(g)),
                       "frac_agree_madin_binary": float(np.mean((ag.pt_anaerobe >= 0.5) == (ag.anaerobe >= 0.5))), "n_madin": int(len(ag))}}
    J["H1_pass"] = bool(J["G1_pass"] and rho > 0 and p1 < 0.05 and r.params[1] > 0 and r.pvalues[1] < 0.05)
    M.to_csv("results/keystone_protraits_genus.csv", index=False); json.dump(J, open(out, "w"), indent=1); print(json.dumps(J))


if __name__ == "__main__":
    main(*sys.argv[1:])
