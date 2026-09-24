"""Are keystone-consensus genera phylogenetically clustered? Resolve each genus to its phylum with NCBI Taxonomy (E-utilities),
then test phylum enrichment among the 25 lowest-p genera vs all modelled genera (Fisher exact, BH).
Outputs: results/keystone_taxonomy.csv, results/keystone_phylum_enrichment.csv."""
import json, time, urllib.request, urllib.parse, re, os
import xml.etree.ElementTree as ET
import pandas as pd
from scipy.stats import fisher_exact
from statsmodels.stats.multitest import multipletests
E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
K = pd.read_csv("results/keystone_consensus.csv")
names = [re.sub(r"^[a-z]__", "", str(x)).strip() for x in K.genus]
NONPROK = {"Arthropoda", "Chordata", "Streptophyta", "Mollusca", "Nematoda", "Ascomycota", "Basidiomycota", "Cnidaria", "Annelida", "Platyhelminthes"}  # eukaryote homonyms of bacterial genera
ids = {}
if os.path.exists("results/keystone_taxonomy.csv"):  # reuse resolved taxids from a previous run
    prev = pd.read_csv("results/keystone_taxonomy.csv", dtype={"taxid": str}); ids = {n: (t if isinstance(t, str) else None) for n, t, ph in zip(prev.genus_clean, prev.taxid, prev.phylum) if not (isinstance(ph, str) and ph in NONPROK)}
for nm in [n for n in names if n not in ids]:
    try:
        r = json.load(urllib.request.urlopen(E + "esearch.fcgi?" + urllib.parse.urlencode({"db": "taxonomy", "term": f"{nm}[Scientific Name] AND genus[Rank] AND (Bacteria[Organism] OR Archaea[Organism])", "retmode": "json"}), timeout=30))
        l = r["esearchresult"]["idlist"]; ids[nm] = l[0] if l else None
    except Exception: ids[nm] = None
    time.sleep(0.35)
found = [i for i in ids.values() if i]
phy = {}
for i in range(0, len(found), 100):
    x = urllib.request.urlopen(E + "efetch.fcgi?" + urllib.parse.urlencode({"db": "taxonomy", "id": ",".join(found[i:i+100]), "retmode": "xml"}), timeout=60).read().decode()
    for tx in ET.fromstring(x).findall("Taxon"):
        ph = [t.findtext("ScientificName") for t in tx.findall("LineageEx/Taxon") if t.findtext("Rank") == "phylum"]
        phy[tx.findtext("TaxId")] = ph[0] if ph else None
    time.sleep(0.4)
K["genus_clean"] = names; K["taxid"] = [ids.get(n) for n in names]; K["phylum"] = [phy.get(t) for t in K.taxid]
K.to_csv("results/keystone_taxonomy.csv", index=False)
K2 = K.dropna(subset=["phylum"]).sort_values("p"); top = set(K2.genus_clean[:25])
rows = []
for ph, g in K2.groupby("phylum"):
    a = len(set(g.genus_clean) & top); b = len(g) - a; c = len(top) - a; d = len(K2) - len(top) - b
    OR, p = fisher_exact([[a, b], [c, d]], alternative="greater"); rows.append({"phylum": ph, "top25": a, "all": len(g), "odds_ratio": OR, "p": p})
F = pd.DataFrame(rows); F["q_bh"] = multipletests(F.p, method="fdr_bh")[1]; F = F.sort_values("p")
F.to_csv("results/keystone_phylum_enrichment.csv", index=False)
print(K.phylum.notna().sum(), "of", len(K), "resolved"); print(F.head(8).to_string(index=False))
