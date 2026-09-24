"""Head-to-head vs MDSINE2 Source Data (Nature Microbiology 2025, Fig. 3) on the official metric.
Usage: python bench_mdsine2.py healthy|uc
"""
import sys, json
import numpy as np, pandas as pd
from scipy.stats import wilcoxon
sys.path.insert(0, "src")
from microtwin.popforecast import forecast

cohort = sys.argv[1]; ALL = len(sys.argv) > 2 and sys.argv[2] == "all"
src = f"data/raw/mdsine2_sourcedata/fig3_{cohort}_absolute.csv"
raw = "data/raw/mdsine2" if cohort == "healthy" else "data/raw/mdsine2_uc"
LB, EPS = 1e-5, 1e3
d = pd.read_csv(src)
meta = pd.read_csv(f"{raw}/metadata.tsv", sep="\t").set_index("sampleID")
qpcr = pd.read_csv(f"{raw}/qpcr.tsv", sep="\t", index_col=0)
counts = pd.read_csv(f"{raw}/counts.tsv", sep="\t", index_col=0)
T = d[d.Method == d.Method.iloc[0]]
days = {}
for s, g in T.groupby("HeldoutSubjectId"):
    th = np.log10(g.groupby("TimePoint").Truth.sum().values + 1)
    m = meta[meta.subject.astype(str) == str(s)]
    m = m[m.index.isin(qpcr.index) & m.index.isin(counts.columns)].sort_values("time")
    mine = np.log10(qpcr.loc[m.index].mean(1).values)
    best = min(range(0, len(mine) - len(th) + 1), key=lambda k: np.mean(np.abs(mine[k:k + len(th)] - th)))
    days[s] = m.time.values[best:best + len(th)]
    print("subject", s, "offset", best, "fit mae", round(float(np.mean(np.abs(mine[best:best + len(th)] - th))), 3))
d["day"] = [days[s][k] for s, k in zip(d.HeldoutSubjectId, d.TimePoint)]


def err_df(df, col="Pred"):
    df = df if ALL else df[df.Truth > LB]
    return df.groupby(["HeldoutSubjectId", "TaxonIdx"]).apply(
        lambda g: np.sqrt(np.mean((np.log10(g[col] + EPS) - np.log10(g.Truth + EPS)) ** 2)), include_groups=False)


E = {m: err_df(g) for m, g in d.groupby("Method")}
T = d[d.Method == d.Method.iloc[0]]
series = {k: (g.sort_values("day").day.values, g.sort_values("day").Truth.values)
          for k, g in T.groupby(["HeldoutSubjectId", "TaxonIdx"])}
subs = sorted(T.HeldoutSubjectId.unique()); taxa = sorted(T.TaxonIdx.unique())
rows = {}
for s in subs:
    for j in taxa:
        dy, tr = series[(s, j)]
        p = forecast([series[(o, j)] for o in subs if o != s], dy, tr[0], 0, EPS, True)
        k = np.ones(len(tr), bool) if ALL else tr > LB
        if k.any():
            rows[(s, j)] = float(np.sqrt(np.mean((p[k] - np.log10(tr[k] + EPS)) ** 2)))
ours = pd.Series(rows); E["PresenceConditionalPopulation (ours)"] = ours
summary = {}
for m, e in sorted(E.items(), key=lambda kv: kv[1].median()):
    e2 = e.loc[ours.index]
    r = {"median": float(e2.median()), "mean": float(e2.mean()), "n": int(len(e2))}
    if m != "PresenceConditionalPopulation (ours)":
        r["ours_better_pairs"] = int((ours < e2).sum()); r["wilcoxon_p"] = float(wilcoxon(ours, e2).pvalue); dd = ours - e2; r["mean_diff_ours_minus"] = float(dd.mean()); r["median_diff_ours_minus"] = float(dd.median()); r["wilcoxon_p_ours_lower"] = float(wilcoxon(ours, e2, alternative="less").pvalue)
    summary[m] = r
    print(f"{m:40s} median {r['median']:.3f} mean {r['mean']:.3f}", {k: v for k, v in r.items() if k in ('ours_better_pairs', 'wilcoxon_p')})
json.dump(summary, open(f"results/mdsine2_headtohead_{cohort}{'_alltimepoints' if ALL else ''}.json", "w"), indent=1)
