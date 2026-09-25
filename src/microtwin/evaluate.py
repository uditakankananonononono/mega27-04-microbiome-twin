"""Cross-validated benchmark of composition predictors."""
from __future__ import annotations

import time

import numpy as np

from .data import bray_curtis
from .models import CNODE, CNODE2, GLVSteady, GraphTwin, PresenceMean, predict_torch, train_torch

EPOCHS = {"cnode": 200, "cnode2": 200, "glv": 200, "graphtwin": 150}


def kfold_indices(n: int, k: int, seed: int = 0) -> list[np.ndarray]:
    idx = np.random.default_rng(seed).permutation(n)
    return [f for f in np.array_split(idx, k) if len(f)]


def fit_predict(name: str, Ztr, Ptr, Zte, seed=0):
    n = Ztr.shape[1]
    if name == "presence_mean":
        return PresenceMean().fit(Ztr, Ptr).predict(Zte)
    if name == "cnode":
        m = CNODE(n)
    elif name == "cnode2":
        m = CNODE2(n)
    elif name == "lgbm":
        return fit_predict_lgbm(Ztr, Ptr, Zte, seed=seed)
    elif name == "glv":
        m = GLVSteady(n)
    elif name == "graphtwin":
        m = GraphTwin(n, prior=Ptr.mean(0))
    elif name == "graphtwin2":
        return fit_predict_twinstack(Ztr, Ptr, Zte, seed=seed)
    elif name == "graphtwin2b":
        return fit_predict_conststack(Ztr, Ptr, Zte, seed=seed)
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
            # numerical-safety: RK4 integrators can explode on tiny/degenerate
            # folds; non-finite rows fall back to the presence-mean null fit on
            # the same train split (deterministic, disclosed). Never triggered
            # on the committed v1/v2 benchmark runs.
            bad = ~np.isfinite(pred).all(1)
            if bad.any():
                fb = PresenceMean().fit(Z[tr], P[tr]).predict(Z[fold])
                pred[bad] = fb[bad]
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
from .models import (CNODE, ConstStack, GLVSteady, GraphTwin, PresenceMean, TwinStack,
                     bc_loss, predict_torch, train_torch)

def _fit_base(name, Ztr, Ptr, seed=0, batch=32):
    n = Ztr.shape[1]
    if name == "presence_mean":
        return PresenceMean().fit(Ztr, Ptr)
    m = {"cnode": CNODE(n), "glv": GLVSteady(n), "graphtwin": GraphTwin(n, prior=Ptr.mean(0))}[name]
    lr = 0.01 if name != "graphtwin" else 0.005
    epochs = {"cnode": 200, "glv": 200, "graphtwin": 150}[name]
    return train_torch(m, Ztr, Ptr, epochs=epochs, lr=lr, seed=seed, batch=batch)

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
            # inner OOF fits are gate-training data only (pre-reg locks epochs
            # and seeds, not inner batch size); full-batch is ~36x faster
            m = _fit_base(b, Ztr[itr], Ptr[itr], seed=seed, batch=max(32, len(itr)))
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


def fit_predict_conststack(Ztr, Ptr, Zte, inner=5, seed=0, drop_margin=0.05):
    """graphtwin2b per PREREG_graphtwin2b: inner-OOF base selection + constant weights."""
    from .evaluate import kfold_indices
    from .data import bray_curtis
    oof = {b: np.zeros((len(Ztr), Ztr.shape[1])) for b in TwinStack.BASES}
    for fold in kfold_indices(len(Ztr), inner, seed=seed):
        itr = np.setdiff1d(np.arange(len(Ztr)), fold)
        for b in TwinStack.BASES:
            m = _fit_base(b, Ztr[itr], Ptr[itr], seed=seed, batch=max(32, len(itr)))
            oof[b][fold] = _predict_base(b, m, Ztr[fold])
    for b in TwinStack.BASES:
        if b == "presence_mean":
            continue
        bad = ~np.isfinite(oof[b]).all(1)
        if bad.any():
            oof[b][bad] = oof["presence_mean"][bad]
    oof_med = {b: float(np.median(bray_curtis(oof[b], Ptr))) for b in TwinStack.BASES}
    best = min(oof_med.values())
    keep = [b for b in TwinStack.BASES if oof_med[b] <= best + drop_margin]
    for must in (min(oof_med, key=oof_med.get), "presence_mean"):
        if must not in keep:
            keep.append(must)
    idx = [TwinStack.BASES.index(b) for b in keep]
    gate = ConstStack(len(keep))
    torch.manual_seed(seed)
    B = torch.tensor(np.stack([oof[b] for b in keep], 1), dtype=torch.float32)
    Pt = torch.tensor(Ptr, dtype=torch.float32)
    opt = torch.optim.Adam(gate.parameters(), lr=0.05)
    for _ in range(400):
        opt.zero_grad()
        bc_loss(gate.combine(B), Pt).backward()
        opt.step()
    gate.eval()
    fitted = {b: _fit_base(b, Ztr, Ptr, seed=seed) for b in keep}
    Bte = np.stack([_predict_base(b, fitted[b], Zte) for b in keep], 1)
    for i in range(len(keep)):
        bad = ~np.isfinite(Bte[:, i]).all(1)
        if bad.any():
            Bte[bad, i] = Bte[bad, keep.index("presence_mean")]
    with torch.no_grad():
        return gate.combine(torch.tensor(Bte, dtype=torch.float32)).numpy()


def fit_predict_lgbm(Ztr, Ptr, Zte, seed=0):
    """Long-form LightGBM composition model per PREREG_arms_cnode2_lgbm."""
    import lightgbm as lgb
    n_taxa = Ztr.shape[1]

    def long_form(Z, P=None):
        n = len(Z)
        X = np.repeat(Z, n_taxa, axis=0)
        taxon = np.tile(np.arange(n_taxa), n)
        X = np.column_stack([X, taxon])
        if P is None:
            return X
        return X, P.ravel()

    Xtr, ytr = long_form(Ztr, Ptr)
    clf = lgb.LGBMRegressor(n_estimators=300, learning_rate=0.05, random_state=seed,
                            categorical_feature=[n_taxa], verbose=-1)
    clf.fit(Xtr, ytr)
    pred = clf.predict(long_form(Zte)).reshape(len(Zte), n_taxa)
    pred = np.clip(pred, 0, None) * (Zte > 0)
    s = pred.sum(1, keepdims=True)
    # degenerate rows (no positive prediction on present taxa) fall back to uniform-over-present
    uni = (Zte > 0) / (Zte > 0).sum(1, keepdims=True)
    ok = s.ravel() > 0
    out = np.where(ok[:, None], pred / np.maximum(s, 1e-12), uni)
    return out
