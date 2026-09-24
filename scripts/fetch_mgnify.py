"""Fetch study-level SSU taxonomy abundance tables from MGnify (EBI) for many studies across biomes.
Writes data/raw/mgnify/<MGYS>.tsv.gz (genus-collapsed counts, taxa x samples) and data/raw/mgnify/manifest.csv.
Only studies with >= MIN_SAMPLES samples and an SSU taxonomy table are kept. Resumable.
"""
import csv, gzip, io, json, os, sys, time, urllib.request, urllib.parse
import pandas as pd
API = "https://www.ebi.ac.uk/metagenomics/api/v1"
OUT = "data/raw/mgnify"; MIN_SAMPLES = 20; TARGET = int(sys.argv[1]) if len(sys.argv) > 1 else 150
BIOMES = ["root:Host-associated:Human:Digestive system", "root:Host-associated:Human:Digestive system:Oral",
          "root:Host-associated:Human:Skin", "root:Host-associated:Mammals", "root:Host-associated:Plants",
          "root:Host-associated:Birds", "root:Host-associated:Fish", "root:Host-associated:Insecta",
          "root:Environmental:Terrestrial:Soil", "root:Environmental:Aquatic:Marine", "root:Environmental:Aquatic:Freshwater",
          "root:Engineered:Wastewater", "root:Engineered:Bioreactor", "root:Environmental:Aquatic:Lentic"]


def get(url, tries=3):
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read()
        except Exception as e:
            time.sleep(2 * (k + 1)); err = e
    raise err


man_path = f"{OUT}/manifest.csv"
done = {}
if os.path.exists(man_path):
    for r in csv.DictReader(open(man_path)): done[r["study"]] = r
seen = set(done)
fh = open(man_path, "a", newline=""); w = csv.writer(fh)
if not done: w.writerow(["study", "secondary_accession", "biome", "n_samples", "n_genera", "file", "source_url", "study_name"]); fh.flush()
kept = sum(1 for r in done.values() if r["file"])
for biome in BIOMES:
    page = 1
    while kept < TARGET:
        url = f"{API}/studies?biome_name={urllib.parse.quote(biome)}&page_size=50&page={page}"
        try: d = json.loads(get(url))
        except Exception as e: print("list fail", biome, e, flush=True); break
        for s in d["data"]:
            sid = s["id"]
            if sid in seen: continue
            seen.add(sid); a = s["attributes"]
            if (a.get("samples-count") or 0) < MIN_SAMPLES: continue
            try:
                dl = json.loads(get(f"{API}/studies/{sid}/downloads"))["data"]
                ssu = [x for x in dl if x["attributes"]["description"]["label"] == "Taxonomic assignments SSU"]
                if not ssu: continue
                src = ssu[-1]["links"]["self"]
                t = pd.read_csv(io.BytesIO(get(src)), sep="\t", index_col=0)
                t = t.select_dtypes("number")
                genus = [(i.split(";g__")[1].split(";")[0] if ";g__" in i and i.split(";g__")[1].split(";")[0] else None) for i in t.index]
                t.index = genus; t = t[t.index.notnull()].groupby(level=0).sum()
                t = t.loc[:, t.sum(0) > 0]
                if t.shape[1] < MIN_SAMPLES or t.shape[0] < 10: continue
                f = f"{OUT}/{sid}.tsv.gz"; t.to_csv(f, sep="\t", compression="gzip")
                w.writerow([sid, a.get("secondary-accession"), biome, t.shape[1], t.shape[0], f, src, (a.get("study-name") or "")[:120]]); fh.flush()
                kept += 1; print(kept, sid, biome, t.shape, flush=True)
            except Exception as e:
                print("skip", sid, type(e).__name__, str(e)[:80], flush=True)
            if kept >= TARGET: break
        if not d["links"].get("next"): break
        page += 1
print("kept", kept)
