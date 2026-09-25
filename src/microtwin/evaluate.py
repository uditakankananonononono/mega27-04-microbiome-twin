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
    elif name == "graphtwin2":
        return fit_predict_twinstack(Ztr, Ptr, Zte, seed=seed)
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
"""Inner-CV stacking for TwinStack, added to evaluate.py."""
import numpy as np, torch
from .models import (CNODE, GLVSteady, GraphTwin, PresenceMean, TwinStack,
                     bc_loss, predict_torch, train_torch)

def _fit_base(name, Ztr, Ptr, seed=0):
    n = Ztr.shape[1]
    if name == "presence_mean":
        return PresenceMean().fit(Ztr, Ptr)
    m = {"cnode": CNODE(n), "glv": GLVSteady(n), "graphtwin": GraphTwin(n, prior=Ptr.mean(0))}[name]
    lr = 0.01 if name != "graphtwin" else 0.005
    epochs = {"cnode": 200, "glv": 200, "graphtwin": 150}[name]
    return train_torch(m, Ztr, Ptr, epochs=epochs, lr=lr, seed=seed)

def _predict_base(name, model, Z):
    if name == "presence_mean":
        return model.predict(Z)
    return predict_torch(model, Z)

def fit_predict_twinstack(Ztr, Ptr, Zte, inner=5, seed=0):
    """Pre-registered stacking: inner OOF base predictions train the gate;
    bases refit on full outer-train; frozen gate combines test predictions."""
    from .evaluate import kfold_indices
    rng = np.random.default_rng(seed)
    oof = {b: np.zeros((len(Ztr), Ztr.shape[1])) for b in TwinStack.BASES}
    for fold in kfold_indices(len(Ztr), inner, seed=seed):
        itr = np.setdiff1d(np.arange(len(Ztr)), fold)
        for b in TwinStack.BASES:
            m = _fit_base(b, Ztr[itr], Ptr[itr], seed=seed)
            oof[b][fold] = _predict_base(b, m, Ztr[fold])
    # numerical-safety fallback: any NaN base prediction falls back to the null's
    for b in TwinStack.BASES:
        if b == "presence_mean":
            continue
        bad = ~np.isfinite(oof[b]).all(1)
        if bad.any():
            oof[b][bad] = oof["presence_mean"][bad]
    gate = TwinStack(Ztr.shape[1], prior=Ptr.mean(0))
    torch.manual_seed(seed)
    Zt = torch.tensor(Ztr, dtype=torch.float32)
    Pt = torch.tensor(Ptr, dtype=torch.float32)
    B = torch.stack([torch.tensor(oof[b], dtype=torch.float32) for b in TwinStack.BASES], 1)
    opt = torch.optim.Adam(gate.parameters(), lr=0.01, weight_decay=1e-4)
    n = len(Ztr)
    for _ in range(200):
        idx = rng.permutation(n)
        for s in range(0, n, 32):
            ib = torch.tensor(idx[s:s + 32])
            opt.zero_grad()
            bc_loss(gate.combine(Zt[ib], B[ib]), Pt[ib]).backward()
            opt.step()
    gate.eval()
    fitted = {b: _fit_base(b, Ztr, Ptr, seed=seed) for b in TwinStack.BASES}
    Bte = np.stack([_predict_base(b, fitted[b], Zte) for b in TwinStack.BASES], 1)
    for i, b in enumerate(TwinStack.BASES):
        if b == "presence_mean":
            continue
        bad = ~np.isfinite(Bte[:, i]).all(1)
        if bad.any():
            Bte[bad, i] = Bte[bad, 0]
    with torch.no_grad():
        return gate.combine(torch.tensor(Zte, dtype=torch.float32),
                            torch.tensor(Bte, dtype=torch.float32)).numpy()
