"""Pre-registered (results/preregistration_disbiome.md) Disbiome literature check of keystone genera.
Source: https://disbiome.ugent.be:8080/experiment (JSON list; cached to data/disbiome/, gitignored)."""
import json, os, sys, urllib.request
import numpy as np, pandas as pd, statsmodels.api as sm

URL = "https://disbiome.ugent.be:8080/experiment"
DROP = ("Candidatus", "uncultured", "unclassified", "[")


def genus_counts(recs):
    d = pd.DataFrame(recs)[["experiment_id", "publication_id", "organism_name"]].dropna(subset=["organism_name"])
    nm = d.organism_name.astype(str).str.strip(); d = d[~nm.str.startswith(DROP) & (nm != "")]
    d["genus"] = d.organism_name.astype(str).str.strip().str.split().str[0].str.capitalize()
    return d.groupby("genus").agg(n_exp=("experiment_id", "nunique"), n_pub=("publication_id", "nunique"))


def main(out="results/keystone_disbiome.json"):
    os.makedirs("data/disbiome", exist_ok=True); f = "data/disbiome/experiment.json"
    if not os.path.exists(f):
        urllib.request.urlretrieve(URL, f)
    recs = json.load(open(f)); c = genus_counts(recs)
    K = pd.read_csv("results/keystone_consensus.csv"); K["genus_clean"] = K.genus.str.replace(r"^[a-z]__", "", regex=True).str.strip()
    K = K.join(c, on="genus_clean"); K[["n_exp", "n_pub"]] = K[["n_exp", "n_pub"]].fillna(0).astype(int); K["kscore"] = -np.log10(K.p)
    X = sm.add_constant(pd.DataFrame({"kscore": K.kscore, "log_studies": np.log(K.studies)}))
    ml = sm.NegativeBinomial(K.n_exp, X).fit(disp=0); a1 = sm.GLM(K.n_exp, X, family=sm.families.NegativeBinomial(alpha=1.0)).fit()
    mp = sm.NegativeBinomial(K.n_pub, X).fit(disp=0)
    J = {"tool": "Disbiome (disbiome.ugent.be experiment API)", "n_records": len(recs), "n_genera": int(len(K)), "n_genera_present": int((K.n_exp > 0).sum()),
         "G1_pass": bool((K.n_exp > 0).sum() >= 150),
         "ml": {"alpha": float(ml.params["alpha"]), "coef_kscore": float(ml.params["kscore"]), "p_kscore": float(ml.pvalues["kscore"])},
         "alpha1": {"coef_kscore": float(a1.params["kscore"]), "p_kscore": float(a1.pvalues["kscore"])},
         "publications_ml": {"coef_kscore": float(mp.params["kscore"]), "p_kscore": float(mp.pvalues["kscore"])},
         "top2_keystones": K.nsmallest(2, "p")[["genus_clean", "n_exp"]].values.tolist()}
    J["D1_pass"] = bool(J["G1_pass"] and J["ml"]["coef_kscore"] > 0 and J["ml"]["p_kscore"] < 0.05)
    K[["genus_clean", "kscore", "studies", "n_exp", "n_pub"]].to_csv("results/keystone_disbiome_genus.csv", index=False)
    json.dump(J, open(out, "w"), indent=1, default=str); print(json.dumps(J, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:])
