"""Pre-registered (results/preregistration_gglasso.md): anaerobe-keystone under graphical-lasso networks (gglasso).
Run repeatedly: fits studies not yet cached (time budget via argv[1] seconds), then fits the model when all studies are done."""
import json, os, sys, time
import numpy as np, pandas as pd, statsmodels.formula.api as smf
from scipy.stats import spearmanr

CACHE = "results/keystone_gglasso_per_study.csv.gz"; LAM = 0.1


def filt(path):
    X = pd.read_csv(path, sep="\t", index_col=0).T
    X = X.loc[X.sum(1) > 0]; X = X.loc[:, (X > 0).mean(0) >= 0.05]; X = X.loc[X.sum(1) > 0]
    if X.shape[1] > 150: X = X[X.columns[np.argsort(-(X > 0).mean(0).values)[:150]]]; X = X.loc[X.sum(1) > 0]
    if len(X) > 400: X = X.sample(400, random_state=0)
    return X


def clr_corr(X):
    L = np.log(X.values + 1.0); C = L - L.mean(1, keepdims=True)
    C = C[:, C.std(0) > 0]; return np.corrcoef(C.T), C.shape[0], C.std(0) > 0


def pcor_degree(Theta):
    d = np.sqrt(np.diag(Theta)); R = -Theta / np.outer(d, d); np.fill_diagonal(R, 0); return np.abs(R).sum(1)


def fit_study(path):
    from gglasso.problem import glasso_problem
    X = filt(path); S, n, keep = clr_corr(X); names = X.columns[keep]
    P = glasso_problem(S, N=n, reg_params={"lambda1": LAM}, latent=False, do_scaling=False); P.solve(verbose=False)
    deg = pcor_degree(P.solution.precision_); thr = np.quantile(deg, 0.9)
    return pd.DataFrame({"genus": names, "gl_degree": deg, "top_gl": deg >= thr})


def main(budget=100):
    man = pd.read_csv("data/raw/mgnify/manifest.csv"); t0 = time.time()
    done = pd.read_csv(CACHE) if os.path.exists(CACHE) else pd.DataFrame(columns=["study", "genus", "gl_degree", "top_gl"])
    for r in man.itertuples():
        if r.study in set(done.study) or not os.path.exists(r.file): continue
        if time.time() - t0 > budget: break
        try:
            d = fit_study(r.file); d.insert(0, "study", r.study)
        except Exception as e:
            d = pd.DataFrame({"study": [r.study], "genus": [None], "gl_degree": [np.nan], "top_gl": [None]}); print(r.study, "FAILED", e)
        done = pd.concat([done, d]); done.to_csv(CACHE, index=False)
    n_done = done.study.nunique(); print("studies cached", n_done, "of", len(man))
    if n_done < len(man): return
    ok = done.dropna(subset=["genus"]); A = pd.read_csv("results/keystone_genus_abundance.csv.gz")
    K = pd.read_csv("results/keystone_kegg_genus.csv")[["genus", "GAI"]].dropna().drop_duplicates("genus")
    D = ok.merge(A, on=["study", "genus"]).merge(K, on="genus"); D["lra"] = np.log10(D.mean_ra + 1e-6); D["top"] = D.top_gl.astype(str).str.lower().eq("true").astype(int)
    D = D[D.groupby("study").top.transform("sum") > 0]
    m = smf.logit("top ~ GAI + lra + prevalence + C(study)", D).fit(disp=0, cov_type="cluster", cov_kwds={"groups": pd.factorize(D.study)[0]}, maxiter=200)
    R = pd.read_csv("results/keystone_per_study.csv.gz")[["study", "genus", "top"]].rename(columns={"top": "top_ridge"})
    B = ok.merge(R, on=["study", "genus"]); a = B.top_gl.astype(str).str.lower().eq("true"); b = B.top_ridge.astype(bool)
    po = float((a == b).mean()); pe = float(a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean())); kappa = (po - pe) / (1 - pe)
    C = pd.read_csv("results/keystone_consensus.csv")[["genus", "frac_top"]]
    gf = ok.assign(t=ok.top_gl.astype(str).str.lower().eq("true")).groupby("genus").agg(n=("study", "nunique"), f=("t", "mean")).reset_index()
    gf = gf[gf.n >= 20].merge(C, on="genus")
    J = {"tool": "gglasso graphical lasso (Schaipp et al. 2021)", "lambda1": LAM, "n_studies_solved": int(ok.study.nunique()), "G1_pass": bool(ok.study.nunique() >= 140),
         "n_rows": int(len(D)), "coef_GAI": float(m.params["GAI"]), "p_GAI": float(m.pvalues["GAI"]),
         "coef_lra": float(m.params["lra"]), "coef_prevalence": float(m.params["prevalence"]),
         "kappa_vs_ridge": kappa, "n_shared_rows": int(len(B)), "spearman_genus_frac_vs_ridge": [float(x) for x in spearmanr(gf.f, gf.frac_top)], "n_genera_ge20": int(len(gf))}
    J["H1_pass"] = bool(J["G1_pass"] and J["coef_GAI"] > 0 and J["p_GAI"] < 0.05)
    json.dump(J, open("results/keystone_gglasso.json", "w"), indent=1); print(json.dumps(J))


if __name__ == "__main__":
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 100)
