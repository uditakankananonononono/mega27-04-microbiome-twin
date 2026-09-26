"""T1 (PREREG_twindiscovery.md): GraphTwin gate out-strength keystone replication.
Per MGnify amplicon study from the audit set (>= 30 samples, >= 20 genera after the audit caps)
plus the cNODE Human_Gut table: train GraphTwin with the locked v1 recipe (d=32, 2 layers,
150 epochs, lr 0.005, seed 0) on the FULL study, score each genus by gate out-strength
(mean over targets of sigmoid(e_target^T U e_source)), then the same top-decile / binomial /
BH-FDR consensus and one-sided Fisher phylum enrichment (GTDB v232) as keystone_mgnify.py /
keystone_gtdb.py. Usage: python3 scripts/twindiscovery_t1.py [epochs] [only_study]"""
import json, os, sys
import numpy as np, pandas as pd, torch
from scipy.stats import binomtest, fisher_exact
sys.path.insert(0, "src")
from microtwin.models import GraphTwin, train_torch

EPOCHS = int(sys.argv[1]) if len(sys.argv) > 1 else 150
ONLY = sys.argv[2] if len(sys.argv) > 2 else None

def load_capped(path):
    X = pd.read_csv(path, sep="\t", index_col=0).T
    X = X.loc[X.sum(1) > 0]; X = X.loc[:, (X > 0).mean(0) >= 0.05]; X = X.loc[X.sum(1) > 0]
    if X.shape[1] > 150: X = X[X.columns[np.argsort(-(X > 0).mean(0).values)[:150]]]; X = X.loc[X.sum(1) > 0]
    if len(X) > 400: X = X.sample(400, random_state=0)
    return X

def fit_gate_outstrength(X):
    P = X.values / X.values.sum(1, keepdims=True); Z = (P > 0).astype(float)
    m = GraphTwin(X.shape[1], prior=P.mean(0))
    train_torch(m, Z, P, epochs=EPOCHS, lr=0.005, seed=0)
    with torch.no_grad():
        gate = torch.sigmoid(m.emb @ m.U @ m.emb.T).numpy()  # [target, source]
    np.fill_diagonal(gate, np.nan)
    return np.nanmean(gate, axis=0)  # out-strength per source genus

SHARD = int(os.environ.get("T1_SHARD", "0")); NSHARD = int(os.environ.get("T1_NSHARD", "1"))
PART = f"results/twindiscovery_t1_partial{'_shard' + str(SHARD) if NSHARD > 1 else ''}.csv"
man = pd.read_csv("data/raw/mgnify/manifest.csv")
man["amplicon"] = ~man.study_name.str.lower().str.contains("assembl")
done = set()
if ONLY is None:
    _parts = sorted(_glob.glob("results/twindiscovery_t1_partial*.csv"))
    for _p in _parts:
        done |= set(pd.read_csv(_p).study.unique())
    if done:
        print(f"resuming: {len(done)} studies already done across {len(_parts)} partials", flush=True)
pf = open(PART, "a") if ONLY is None else None
rows = []
ELIG = [r for r in man.itertuples() if r.amplicon]
for ei, r in enumerate(ELIG):
    if ONLY and r.study != ONLY: continue
    if NSHARD > 1 and ei % NSHARD != SHARD: continue
    if r.study in done: continue
    if not os.path.exists(r.file):
        print(r.study, "MISSING FILE", flush=True); continue
    X = load_capped(r.file)
    if len(X) < 30 or X.shape[1] < 20:
        print(r.study, "SKIP", X.shape, flush=True); continue
    s = fit_gate_outstrength(X)
    thr = np.quantile(s, 0.9)
    for name, v in zip(X.columns, s):
        if pf is not None: pf.write(f"{r.study},{r.biome.split(':')[-1]},{name},{float(v):.6f},{bool(v >= thr)}\n")
        else: rows.append((r.study, r.biome.split(":")[-1], name, float(v), bool(v >= thr)))
    if pf is not None: pf.flush()
    print(r.study, X.shape, "done", flush=True)

if ONLY is None:
    Xg = pd.read_csv("data/raw/cnode/Human_Gut.csv", index_col=0)
    Xg = Xg.loc[Xg.sum(1) > 0]
    s = fit_gate_outstrength(Xg)
    thr = np.quantile(s, 0.9)
    if "cNODE_Human_Gut" not in done:
        for name, v in zip(Xg.columns, s):
            pf.write(f"cNODE_Human_Gut,Human:Digestive system,{name},{float(v):.6f},{bool(v >= thr)}\n")
        pf.flush()
    print("cNODE_Human_Gut", Xg.shape, "done", flush=True)

if ONLY is not None:
    D = pd.DataFrame(rows, columns=["study", "biome", "genus", "gate_out_strength", "top"])
    print(D.sort_values("gate_out_strength", ascending=False).head(8).to_string(index=False)); sys.exit(0)

if pf is not None: pf.close()
import glob as _glob
if ONLY is None:
    open(f"results/twindiscovery_t1_shard{SHARD}.done", "w").write("done")
if NSHARD > 1 and len(_glob.glob("results/twindiscovery_t1_shard*.done")) < NSHARD:
    print("waiting for other shards; consensus not computed", flush=True); sys.exit(0)
D = pd.concat([pd.read_csv(f, names=["study", "biome", "genus", "gate_out_strength", "top"])
               for f in sorted(_glob.glob("results/twindiscovery_t1_partial*.csv"))]).drop_duplicates(["study", "genus"])
D.to_csv("results/twindiscovery_t1_per_study.csv.gz", index=False)
g = D.groupby("genus").agg(studies=("study", "nunique"), top=("top", "sum")).reset_index()
g = g[g.studies >= 20]
g["frac_top"] = g.top / g.studies
g["p"] = [binomtest(int(t), int(n), 0.1, alternative="greater").pvalue for t, n in zip(g.top, g.studies)]
o = np.argsort(g.p.values); m_ = len(g); q = np.empty(m_)
q[o] = np.minimum.accumulate((g.p.values[o] * m_ / np.arange(1, m_ + 1))[::-1])[::-1]
g["q_bh"] = np.minimum(q, 1); g = g.sort_values("p")
g.to_csv("results/twindiscovery_t1_consensus.csv", index=False)

gt = pd.read_csv("results/keystone_gtdb.csv")[["genus", "gtdb_phylum"]]
gg = g.merge(gt, on="genus", how="inner")
top25 = set(gg.nsmallest(25, "p").genus)
ph = []
for phy, sub in gg.groupby("gtdb_phylum"):
    a = sub.genus.isin(top25).sum(); b = 25 - a
    c = (~sub.genus.isin(top25)).sum(); d = len(gg) - 25 - c
    ph.append((phy, int(a), len(sub), fisher_exact([[a, b], [c, d]], alternative="greater").pvalue))
PH = pd.DataFrame(ph, columns=["phylum", "top25", "all", "p"]).sort_values("p")
o = np.argsort(PH.p.values); m2 = len(PH); q2 = np.empty(m2)
q2[o] = np.minimum.accumulate((PH.p.values[o] * m2 / np.arange(1, m2 + 1))[::-1])[::-1]
PH["q_bh"] = np.minimum(q2, 1)
PH.to_csv("results/twindiscovery_t1_phylum.csv", index=False)
best = PH.iloc[0]
out = {"studies": int(D.study.nunique()), "genera": int(len(g)),
       "top_phylum": best.phylum, "top_phylum_q": float(best.q_bh),
       "desulfobacterota_q": float(PH.loc[PH.phylum == "Desulfobacterota", "q_bh"].iloc[0]) if (PH.phylum == "Desulfobacterota").any() else None,
       "t1_pass": bool((PH.q_bh < 0.05).any()),
       "summary": ""}
out["summary"] = (f"T1: {out['studies']} studies, {out['genera']} genera. "
                  f"Top enrichment: {best.phylum} q={best.q_bh:.3g}. "
                  f"Desulfobacterota q={out['desulfobacterota_q']}. "
                  f"{'REPLICATION PASS (some phylum FDR<0.05)' if out['t1_pass'] else 'NULL - redirect to SHAP centrality per pre-reg'}")
json.dump(out, open("results/twindiscovery_t1.json", "w"), indent=2)
print(out["summary"])
