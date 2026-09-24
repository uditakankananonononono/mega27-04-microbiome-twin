"""Summarise results/mgnify_audit.csv: BH-FDR across studies, per-biome fractions, figure."""
import json
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
a = pd.read_csv("results/mgnify_audit.csv").drop_duplicates("study")
p = a.wilcoxon_p.values; o = np.argsort(p); m = len(p)
q = np.empty(m); q[o] = np.minimum.accumulate((p[o] * m / np.arange(1, m + 1))[::-1])[::-1]; a["q_bh"] = np.minimum(q, 1)
a["biome_short"] = a.biome.str.split(":").str[-1]
a["int_wins"] = (a.q_bh < 0.05) & (a.gain > 0); a["prior_wins"] = (a.q_bh < 0.05) & (a.gain < 0)
g = a.groupby("biome_short").agg(studies=("study", "size"), int_wins=("int_wins", "sum"), prior_wins=("prior_wins", "sum"),
                                 median_gain=("gain", "median"), median_prior_bc=("median_prior", "median")).reset_index()
s = {"studies": int(m), "interaction_better_fdr05": int(a.int_wins.sum()), "prior_better_fdr05": int(a.prior_wins.sum()),
     "no_difference": int(m - a.int_wins.sum() - a.prior_wins.sum()), "median_gain": float(a.gain.median()),
     "median_relative_gain": float((a.gain / a.median_prior).median()), "per_biome": g.to_dict("records")}
json.dump(s, open("results/mgnify_audit_summary.json", "w"), indent=1); a.to_csv("results/mgnify_audit_fdr.csv", index=False)
print(json.dumps({k: v for k, v in s.items() if k != "per_biome"}, indent=1)); print(g.to_string(index=False))
fig, ax = plt.subplots(figsize=(9, 5))
for i, (b, h) in enumerate(a.groupby("biome_short")):
    x = np.full(len(h), i) + np.random.default_rng(0).uniform(-0.25, 0.25, len(h))
    ax.scatter(x, h.gain / h.median_prior, c=np.where(h.int_wins, "#c0392b", np.where(h.prior_wins, "#2c3e50", "#95a5a6")), s=18)
ax.axhline(0, color="k", lw=0.8); ax.set_xticks(range(a.biome_short.nunique())); ax.set_xticklabels(sorted(a.biome_short.unique()), rotation=20)
ax.set_ylabel("relative gain of interaction model\n(median BC prior - interaction) / prior"); ax.set_title(f"Interaction audit across {m} MGnify studies (red: interactions better, FDR<0.05)")
plt.tight_layout(); plt.savefig("results/figures/fig_mgnify_audit.png", dpi=150)
