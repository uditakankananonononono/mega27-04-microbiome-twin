"""Cross-validated benchmark of composition predictors."""
from __future__ import annotations

import time

import numpy as np

from .data import bray_curtis
from .models import CNODE, GLVSteady, GraphTwin, PresenceMean, predict_torch, train_torch

EPOCHS = {"cnode": 200, "glv": 200, "graphtwin": 150}


def kfold_indices(n: int, k: int, seed: int = 0) -> list[np.ndarray]:
    idx = np.random.default_rng(seed).permutation(n)
    return [f for f in np.array_split(idx, k) if len(f)]


def fit_predict(name: str, Ztr, Ptr, Zte, seed=0):
    n = Ztr.shape[1]
    if name == "presence_mean":
        return PresenceMean().fit(Ztr, Ptr).predict(Zte)
    if name == "cnode":
        m = CNODE(n)
    elif name == "glv":
        m = GLVSteady(n)
    elif name == "graphtwin":
        m = GraphTwin(n, prior=Ptr.mean(0))
    else:
        raise ValueError(name)
    lr = 0.01 if name != "graphtwin" else 0.005
    train_torch(m, Ztr, Ptr, epochs=EPOCHS[name], lr=lr, seed=seed)
    return predict_torch(m, Zte)


def cross_validate(Z, P, models, k: int, seed: int = 0) -> dict[str, np.ndarray]:
    """Per-sample out-of-fold Bray-Curtis error for each model (same folds)."""
    err = {m: np.full(len(Z), np.nan) for m in models}
    for fold in kfold_indices(len(Z), k, seed):
        tr = np.setdiff1d(np.arange(len(Z)), fold)
        for m in models:
            pred = fit_predict(m, Z[tr], P[tr], Z[fold], seed=seed)
            err[m][fold] = bray_curtis(pred, P[fold])
    return err


def paired_bootstrap(a: np.ndarray, b: np.ndarray, n_boot: int = 5000, seed: int = 0):
    """CI of median(a) - median(b) under paired resampling of samples."""
    rng = np.random.default_rng(seed)
    n = len(a); d = []
    for _ in range(n_boot):
        i = rng.integers(0, n, n)
        d.append(np.median(a[i]) - np.median(b[i]))
    d = np.array(d)
    return float(np.median(a) - np.median(b)), float(np.quantile(d, 0.025)), float(np.quantile(d, 0.975))
