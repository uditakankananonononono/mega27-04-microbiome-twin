"""Pre-registered (results/preregistration_xgboost.md): out-of-sample value of GAI under XGBoost."""
import json
import numpy as np, pandas as pd
from scipy.stats import binomtest
from sklearn.model_selection import KFold
from xgboost import XGBRegressor


def data():
    K = pd.read_csv("results/keystone_kegg_genus.csv").dropna(subset=["GAI"]).drop_duplicates("genus_clean")
    ab = pd.read_csv("results/keystone_genus_abundance.csv.gz").groupby("genus").mean_ra.mean().rename("mean_ra")
    E = pd.read_csv("results/keystone_ena_counts.csv")[["genus_clean", "ena_assemblies"]]
    M = K.merge(ab, left_on="genus_clean", right_index=True).merge(E, on="genus_clean").dropna(subset=["mean_ra", "ena_assemblies"])
    M["lra"] = np.log10(M.mean_ra + 1e-6); M["log_ena"] = np.log10(1 + M.ena_assemblies); return M


def oof_r2(X, y, seed):
    pred = np.zeros(len(y))
    for tr, te in KFold(5, shuffle=True, random_state=seed).split(X):
        m = XGBRegressor(n_estimators=300, max_depth=3, learning_rate=0.05, subsample=0.8, colsample_bytree=1.0, random_state=seed)
        m.fit(X[tr], y[tr]); pred[te] = m.predict(X[te])
    return 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()


def main():
    M = data(); y = M.frac_top.values
    full = M[["GAI", "lra", "log_ena"]].values; red = M[["lra", "log_ena"]].values
    d = [(oof_r2(full, y, s), oof_r2(red, y, s)) for s in range(20)]
    delta = np.array([a - b for a, b in d]); npos = int((delta > 0).sum())
    J = {"tool": "XGBoost (gradient-boosted trees)", "n_genera": int(len(M)), "G1_pass": bool(len(M) >= 180),
         "r2_full_mean": float(np.mean([a for a, _ in d])), "r2_reduced_mean": float(np.mean([b for _, b in d])),
         "delta_mean": float(delta.mean()), "n_positive": npos, "sign_test_p": float(binomtest(npos, 20).pvalue)}
    J["X1_pass"] = bool(J["G1_pass"] and J["delta_mean"] > 0 and npos >= 15)
    json.dump(J, open("results/keystone_xgboost.json", "w"), indent=1); print(json.dumps(J))


if __name__ == "__main__":
    main()
