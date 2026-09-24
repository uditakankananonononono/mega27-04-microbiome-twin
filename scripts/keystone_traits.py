"""Do keystone genera share physiological traits? Madin et al. 2020 (Sci Data 7:170) bacterial/archaeal trait database,
condensed_species_NCBI.csv (github.com/bacteria-archaea-traits). Species traits aggregated to genus
(anaerobe = anaerobic/obligate anaerobic share; gram-negative, motile, sporulating shares; median genome size, GC, doubling time).
Tests over the 248 modelled genera (results/keystone_taxonomy.csv): Spearman(trait, frac_top) and Mann-Whitney top-25 vs rest; BH across traits.
Output: results/keystone_traits.csv, results/keystone_traits_tests.csv."""
import numpy as np, pandas as pd
from scipy.stats import spearmanr, mannwhitneyu
from statsmodels.stats.multitest import multipletests
M = pd.read_csv("data/traits/condensed_species_NCBI.csv", low_memory=False)
M["anaerobe"] = M.metabolism.map(lambda m: np.nan if pd.isna(m) else float("anaerob" in m and "facultative" not in m))
M["gram_neg"] = M.gram_stain.map(lambda m: np.nan if pd.isna(m) else float(m == "negative"))
M["motile"] = M.motility.map(lambda m: np.nan if pd.isna(m) else float(m in ("yes", "flagella", "gliding", "axial filament")))
M["spore"] = M.sporulation.map(lambda m: np.nan if pd.isna(m) else float(m == "yes"))
TR = ["anaerobe", "gram_neg", "motile", "spore", "genome_size", "gc_content", "doubling_h"]
agg = M.groupby("genus").agg({**{t: "mean" for t in TR[:4]}, **{t: "median" for t in TR[4:]}})
K = pd.read_csv("results/keystone_taxonomy.csv").merge(agg, left_on="genus_clean", right_index=True, how="left")
K.to_csv("results/keystone_traits.csv", index=False)
K = K.sort_values("p"); K["is_top25"] = False; K.loc[K.index[:25], "is_top25"] = True
rows = []
for t in TR:
    s = K.dropna(subset=[t]); rho, p = spearmanr(s[t], s.frac_top)
    a, b = s[s.is_top25][t], s[~s.is_top25][t]
    mw = mannwhitneyu(a, b).pvalue if len(a) > 2 else np.nan
    rows.append({"trait": t, "n": len(s), "n_top25": len(a), "spearman_rho": rho, "p_spearman": p, "top25_mean": a.mean(), "rest_mean": b.mean(), "p_mw": mw})
R = pd.DataFrame(rows); R["q_spearman"] = multipletests(R.p_spearman, method="fdr_bh")[1]; R["q_mw"] = multipletests(R.p_mw.fillna(1), method="fdr_bh")[1]
R.to_csv("results/keystone_traits_tests.csv", index=False); print(R.round(4).to_string())
# Confound check: rank-OLS (frac_top ~ anaerobe + genome_size + log studies) and permutation of anaerobe within studies-quintiles
import statsmodels.formula.api as smf, json
from scipy.stats import rankdata
S = K.dropna(subset=["anaerobe", "genome_size"]).copy()
for c in ["frac_top", "anaerobe", "genome_size"]: S["r_" + c] = rankdata(S[c])
S["lstud"] = np.log(S.studies)
fit = smf.ols("r_frac_top ~ r_anaerobe + r_genome_size + lstud", S).fit(cov_type="HC3")
rng = np.random.default_rng(0); S["qb"] = pd.qcut(S.studies, 5, labels=False, duplicates="drop")
obs = spearmanr(S.anaerobe, S.frac_top)[0]; null = []
for _ in range(5000):
    perm = S.groupby("qb").anaerobe.transform(lambda x: rng.permutation(x.values)); null.append(spearmanr(perm, S.frac_top)[0])
pp = (1 + sum(abs(x) >= abs(obs) for x in null)) / 5001
out = {"n": len(S), "ols_rank_params": fit.params.to_dict(), "ols_pvalues": fit.pvalues.to_dict(), "strat_perm_rho": obs, "strat_perm_p": pp}
json.dump(out, open("results/keystone_traits_confound.json", "w"), indent=1); print(json.dumps(out, indent=1))
