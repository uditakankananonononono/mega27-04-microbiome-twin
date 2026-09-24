"""Interaction audit: does knowing *which other taxa are present* improve composition prediction
beyond a presence-conditional prior?

Given a samples x taxa abundance matrix P (rows on the simplex) and presence Z = 1[P > 0]:
  prior       p_i(z) ∝ z_i * exp(mu_i),  from the two-way fit log p_si = mu_i + c_s on present entries
  interaction p_i(z) ∝ z_i * exp(mu_i + b_i + sum_j W_ij z_j)
where (b_i, W_i.) is a ridge fit of the residual log p_si - mu_i - c_s on z_s over samples with z_si = 1
(a steady-state generalised Lotka-Volterra form: log-abundance shifts linearly with the assemblage).
Ridge penalty chosen by inner 3-fold CV on the training fold only. Error: Bray-Curtis. K-fold outer CV.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import wilcoxon

LAMBDAS = (1.0, 10.0, 100.0, 1000.0)


def bray_curtis(p, q):
    return np.abs(p - q).sum(-1) / np.maximum((p + q).sum(-1), 1e-12)


def _normalise(logit, Z):
    logit = np.where(Z > 0, logit, -np.inf)
    m = logit.max(1, keepdims=True); m[~np.isfinite(m)] = 0
    e = np.where(Z > 0, np.exp(logit - m), 0.0)
    return e / np.maximum(e.sum(1, keepdims=True), 1e-300)


def _two_way(P, iters=30):
    """No-interaction log-linear fit on present entries: log p_si = mu_i + c_s (c_s absorbs the
    per-sample closure constant, so mu is not biased by which other taxa are present)."""
    Z = P > 0; L = np.log(np.where(Z, P, 1.0)); cnt = Z.sum(0)
    mu = np.where(cnt > 0, (L * Z).sum(0) / np.maximum(cnt, 1), 0.0); c = np.zeros(len(P))
    for _ in range(iters):
        c = ((L - mu) * Z).sum(1) / np.maximum(Z.sum(1), 1)
        mu = np.where(cnt > 0, ((L - c[:, None]) * Z).sum(0) / np.maximum(cnt, 1), mu)
    mu = np.where(cnt > 0, mu, mu[cnt > 0].min() - 5 if (cnt > 0).any() else 0.0)
    return mu, c, L, Z


def fit_prior(P):
    return _two_way(P)[0]


def predict_prior(mu, Z):
    return _normalise(np.broadcast_to(mu, Z.shape).copy(), Z)


def fit_interaction(P, lam, min_n=5):
    mu, c, L, Zb = _two_way(P); Z = Zb.astype(float)
    n, N = P.shape; W = np.zeros((N, N)); b = np.zeros(N)
    for i in range(N):
        rows = Z[:, i] > 0
        if rows.sum() < min_n: continue
        X = Z[rows].copy(); X[:, i] = 0; xm = X.mean(0); Xc = X - xm
        y = L[rows, i] - mu[i] - c[rows]; ym = y.mean()
        A = Xc.T @ Xc + lam * np.eye(N)
        w = np.linalg.solve(A, Xc.T @ (y - ym))
        W[i] = w; b[i] = ym - xm @ w
    return mu, b, W


def predict_interaction(model, Z):
    mu, b, W = model; Zf = Z.astype(float)
    return _normalise(mu + b + Zf @ W.T, Z)


def _folds(n, k, rng):
    idx = rng.permutation(n); return [idx[f::k] for f in range(k)]


def audit(P, k=5, seed=0):
    """Returns dict with per-sample BC errors for prior and interaction models and a paired test."""
    P = np.asarray(P, float); P = P / P.sum(1, keepdims=True)
    keep = (P > 0).sum(0) >= 1; P = P[:, keep]
    rng = np.random.default_rng(seed); n = len(P)
    e_prior = np.zeros(n); e_int = np.zeros(n); lams = []
    for te in _folds(n, k, rng):
        tr = np.setdiff1d(np.arange(n), te); Ptr = P[tr]
        # inner CV for lambda
        best, bl = np.inf, LAMBDAS[-1]
        for lam in LAMBDAS:
            errs = []
            for ite in _folds(len(tr), 3, np.random.default_rng(seed + 1)):
                itr = np.setdiff1d(np.arange(len(tr)), ite)
                m = fit_interaction(Ptr[itr], lam)
                errs.append(bray_curtis(predict_interaction(m, Ptr[ite] > 0), Ptr[ite]))
            s = np.median(np.concatenate(errs))
            if s < best: best, bl = s, lam
        lams.append(bl)
        mu = fit_prior(Ptr); Zte = P[te] > 0
        e_prior[te] = bray_curtis(predict_prior(mu, Zte), P[te])
        e_int[te] = bray_curtis(predict_interaction(fit_interaction(Ptr, bl), Zte), P[te])
    d = e_int - e_prior
    p = float(wilcoxon(e_int, e_prior).pvalue) if np.any(d != 0) else 1.0
    return {"n": n, "taxa": int(P.shape[1]), "median_prior": float(np.median(e_prior)), "median_interaction": float(np.median(e_int)),
            "gain": float(np.median(e_prior) - np.median(e_int)), "int_better_frac": float((d < 0).mean()), "wilcoxon_p": p,
            "lambdas": lams, "e_prior": e_prior.tolist(), "e_int": e_int.tolist()}
