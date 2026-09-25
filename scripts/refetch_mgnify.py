"""Re-download MGnify study tables that are missing from data/raw/mgnify (gitignored cache),
using the source_url recorded in the committed manifest.csv. Processing mirrors fetch_mgnify.py exactly."""
import csv, io, os, time, urllib.request
import pandas as pd

def get(url, tries=3):
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read()
        except Exception:
            time.sleep(2 * (k + 1))
    return None

n_ok = n_fail = 0
for r in csv.DictReader(open("data/raw/mgnify/manifest.csv")):
    if os.path.exists(r["file"]): n_ok += 1; continue
    raw = get(r["source_url"])
    if raw is None: print("FAIL", r["study"], flush=True); n_fail += 1; continue
    try:
        t = pd.read_csv(io.BytesIO(raw), sep="\t", index_col=0)
        t = t.select_dtypes("number")
        genus = [(i.split(";g__")[1].split(";")[0] if ";g__" in i and i.split(";g__")[1].split(";")[0] else None) for i in t.index]
        t.index = genus; t = t[t.index.notnull()].groupby(level=0).sum()
        t = t.loc[:, t.sum(0) > 0]
        t.to_csv(r["file"], sep="\t", compression="gzip")
        n_ok += 1; print("ok", n_ok, r["study"], t.shape, flush=True)
    except Exception as e:
        print("FAIL", r["study"], type(e).__name__, str(e)[:80], flush=True); n_fail += 1
print(f"REFETCH_DONE ok={n_ok} fail={n_fail}", flush=True)
