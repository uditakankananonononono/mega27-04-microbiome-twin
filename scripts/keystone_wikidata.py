"""Pre-registered (results/preregistration_wikidata.md) Wikidata Gram-stain check of ridge keystones."""
import json, os, sys, urllib.parse, urllib.request
import numpy as np, pandas as pd
from scipy.stats import spearmanr

EP = "https://query.wikidata.org/sparql"
Q = """SELECT ?name ?g WHERE { ?t wdt:P105 wd:Q34740 ; wdt:P2597 ?g ; wdt:P225 ?name . }"""
NEG, POS = "Q632006", "Q857288"


def gram_table(bindings):
    rows = [(b["name"]["value"], b["g"]["value"].rsplit("/", 1)[-1]) for b in bindings]
    d = pd.DataFrame(rows, columns=["genus", "q"]); d = d[d.q.isin([NEG, POS])]
    g = d.groupby("genus").q.agg(lambda s: set(s)); g = g[g.map(len) == 1]
    return g.map(lambda s: int(NEG in s)).rename("wd_gram_neg")


def main(out="results/keystone_wikidata.json", cache="results/keystone_wikidata_gram.csv"):
    if not os.path.exists(cache):
        req = urllib.request.Request(EP + "?" + urllib.parse.urlencode({"query": Q}), headers={"Accept": "application/sparql-results+json", "User-Agent": "mega27-research/0.1"})
        gram_table(json.load(urllib.request.urlopen(req, timeout=100))["results"]["bindings"]).to_csv(cache)
    W = pd.read_csv(cache, index_col=0)["wd_gram_neg"]
    T = pd.read_csv("results/keystone_traits.csv").drop_duplicates("genus_clean")
    M = T.merge(W, left_on="genus_clean", right_index=True)
    a = M.dropna(subset=["gram_neg"]); agree = float(np.mean((a.gram_neg >= 0.5) == (a.wd_gram_neg == 1)))
    rho, p = spearmanr(M.frac_top, M.wd_gram_neg)
    J = {"tool": "Wikidata SPARQL (P2597 Gram staining)", "n_wikidata_genera": int(len(W)), "n_matched": int(len(M)),
         "agreement_madin": agree, "n_agreement": int(len(a)), "G1_pass": bool(agree >= 0.8 and len(a) >= 100),
         "spearman_rho": float(rho), "p_two_sided": float(p)}
    J["W0_verdict"] = "replicated" if p >= 0.05 else "contradicted"
    json.dump(J, open(out, "w"), indent=1); print(json.dumps(J))


if __name__ == "__main__":
    main(*sys.argv[1:])
