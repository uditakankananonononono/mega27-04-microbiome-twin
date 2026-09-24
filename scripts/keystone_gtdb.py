"""Replicate keystone phylum/family enrichment with GTDB (release per data/gtdb VERSION) instead of NCBI Taxonomy.
Genus -> GTDB phylum/class/family by majority over bac120 genomes (GTDB genus names; suffixed splits like g__X_A merged to X).
Same test as keystone_taxonomy.py: top-25 lowest-p genera vs all mapped genera, one-sided Fisher, BH.
Download: https://data.gtdb.ecogenomic.org/releases/latest/bac120_taxonomy.tsv.gz"""
import gzip, re, json, collections, pandas as pd
from scipy.stats import fisher_exact
from statsmodels.stats.multitest import multipletests
maps = collections.defaultdict(lambda: collections.Counter())
with gzip.open("data/gtdb/bac120_tax.tsv.gz", "rt") as f:
    for line in f:
        t = dict(x.split("__", 1) for x in line.rstrip("\n").split("\t")[1].split(";"))
        g = re.sub(r"_[A-Z]+$", "", t["g"])
        if g: maps[g][(t["p"], t["c"], t["f"])] += 1
K = pd.read_csv("results/keystone_taxonomy.csv")
def lab(g, i):
    c = maps.get(g)
    if not c: return None
    agg = collections.Counter()
    for k, v in c.items(): agg[re.sub(r"_[A-Z]+$", "", k[i])] += v
    return agg.most_common(1)[0][0]
for i, lvl in enumerate(["gtdb_phylum", "gtdb_class", "gtdb_family"]): K[lvl] = K.genus_clean.map(lambda g: lab(g, i))
K.to_csv("results/keystone_gtdb.csv", index=False)
K2 = K.dropna(subset=["gtdb_phylum"]).sort_values("p"); top = set(K2.genus_clean[:25]); out = {"n_mapped": len(K2), "n_total": len(K)}
for lvl in ["gtdb_phylum", "gtdb_family"]:
    rows = []
    for ph, g in K2.groupby(lvl):
        a = len(set(g.genus_clean) & top); b = len(g) - a; c = len(top) - a; d = len(K2) - len(top) - b
        OR, p = fisher_exact([[a, b], [c, d]], alternative="greater"); rows.append({"taxon": ph, "top25": a, "all": len(g), "odds_ratio": OR, "p": p})
    R = pd.DataFrame(rows); R["q_bh"] = multipletests(R.p, method="fdr_bh")[1]; R = R.sort_values("p")
    R.to_csv(f"results/keystone_{lvl}_enrichment.csv", index=False); out[lvl] = R.head(5).to_dict("records")
out["ncbi_vs_gtdb_phylum_disagreements"] = K2[["genus_clean", "phylum", "gtdb_phylum"]][K2.phylum != K2.gtdb_phylum].values.tolist()
json.dump(out, open("results/keystone_gtdb.json", "w"), indent=1, default=str)
print(out["n_mapped"], out["n_total"]); [print(lvl, r) for lvl in ["gtdb_phylum", "gtdb_family"] for r in out[lvl][:3]]
print(len(out["ncbi_vs_gtdb_phylum_disagreements"]), out["ncbi_vs_gtdb_phylum_disagreements"][:12])
