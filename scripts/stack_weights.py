"""Full-data ConstStack weights per dataset: the interpretable 4-number blend (the named plus point).
Mirrors fit_predict_conststack's inner-OOF selection + weight fit, run once per dataset on all samples.
Usage: python3 scripts/stack_weights.py [dataset ...]"""
import json, sys
import numpy as np, torch
sys.path.insert(0, "src")
from microtwin.evaluate import _fit_base, _predict_base, kfold_indices, TwinStack
from microtwin.data import bray_curtis, load
from microtwin.models import ConstStack, bc_loss

def full_weights(Z, P, inner=5, seed=0, drop_margin=0.05):
    oof = {b: np.zeros((len(Z), Z.shape[1])) for b in TwinStack.BASES}
    for fold in kfold_indices(len(Z), inner, seed=seed):
        itr = np.setdiff1d(np.arange(len(Z)), fold)
        for b in TwinStack.BASES:
            m = _fit_base(b, Z[itr], P[itr], seed=seed, batch=max(32, len(itr)))
            oof[b][fold] = _predict_base(b, m, Z[fold])
    for b in TwinStack.BASES:
        if b == "presence_mean": continue
        bad = ~np.isfinite(oof[b]).all(1)
        if bad.any(): oof[b][bad] = oof["presence_mean"][bad]
    oof_med = {b: float(np.median(bray_curtis(oof[b], P))) for b in TwinStack.BASES}
    best = min(oof_med.values())
    keep = [b for b in TwinStack.BASES if oof_med[b] <= best + drop_margin]
    for must in (min(oof_med, key=oof_med.get), "presence_mean"):
        if must not in keep: keep.append(must)
    gate = ConstStack(len(keep)); torch.manual_seed(seed)
    B = torch.tensor(np.stack([oof[b] for b in keep], 1), dtype=torch.float32)
    Pt = torch.tensor(P, dtype=torch.float32)
    opt = torch.optim.Adam(gate.parameters(), lr=0.05)
    for _ in range(400):
        opt.zero_grad(); bc_loss(gate.combine(B), Pt).backward(); opt.step()
    w = torch.softmax(gate.logits, 0).detach().numpy()
    return {b: float(wi) for b, wi in zip(keep, w)}, oof_med, keep

import os
out = json.load(open("results/stack_weights.json")) if os.path.exists("results/stack_weights.json") else {}
for d in (sys.argv[1:] or ["Drosophila_Gut", "Human_Gut", "Human_Oral", "Ocean", "Soil_Vitro", "Soil_Vivo"]):
    Z, P = load(d)
    w, oof_med, keep = full_weights(Z, P)
    out[d] = {"weights": w, "inner_oof_median": oof_med, "kept_bases": keep}
    print(d, {k: round(v, 3) for k, v in w.items()}, flush=True)
json.dump(out, open("results/stack_weights.json", "w"), indent=1)
