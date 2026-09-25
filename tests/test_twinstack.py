import sys
sys.path.insert(0, "src")
import numpy as np
import torch
from microtwin.models import TwinStack
from microtwin.evaluate import fit_predict_twinstack


def _toy(n=24, taxa=8, seed=0):
    rng = np.random.default_rng(seed)
    Z = (rng.random((n, taxa)) < 0.6).astype(float)
    Z[Z.sum(1) == 0, 0] = 1.0
    P = rng.dirichlet(np.ones(taxa), n) * Z
    P = P / P.sum(1, keepdims=True)
    return Z, P


def test_output_on_simplex():
    Z, _ = _toy()
    gate = TwinStack(Z.shape[1], prior=np.full(Z.shape[1], 1 / Z.shape[1]))
    bases = torch.rand(len(Z), 4, Z.shape[1])
    bases = bases / bases.sum(-1, keepdim=True)
    p = gate.combine(torch.tensor(Z, dtype=torch.float32), bases)
    assert torch.allclose(p.sum(1), torch.ones(len(Z)), atol=1e-5)


def test_zero_init_gives_mean_of_bases():
    Z, _ = _toy()
    gate = TwinStack(Z.shape[1], prior=np.full(Z.shape[1], 1 / Z.shape[1]))
    bases = torch.rand(len(Z), 4, Z.shape[1])
    bases = bases / bases.sum(-1, keepdim=True)
    p = gate.combine(torch.tensor(Z, dtype=torch.float32), bases)
    mean = bases.mean(1)
    mean = mean / mean.sum(-1, keepdim=True)
    assert torch.allclose(p, mean, atol=1e-5)


def test_absence_masking_preserved():
    Z, _ = _toy()
    gate = TwinStack(Z.shape[1], prior=np.full(Z.shape[1], 1 / Z.shape[1]))
    bases = torch.rand(len(Z), 4, Z.shape[1]) * torch.tensor(Z).unsqueeze(1)
    bases = bases / bases.sum(-1, keepdim=True)
    p = gate.combine(torch.tensor(Z, dtype=torch.float32), bases)
    assert (p.detach().numpy()[Z == 0] == 0).all()


def test_fit_predict_smoke():
    Z, P = _toy(n=20, taxa=6)
    pred = fit_predict_twinstack(Z[:16], P[:16], Z[16:], inner=2, seed=0)
    assert pred.shape == (4, 6)
    assert np.allclose(pred.sum(1), 1, atol=1e-5)


def test_conststack_zero_init_is_mean():
    from microtwin.models import ConstStack
    g = ConstStack(3)
    bases = torch.rand(5, 3, 7)
    bases = bases / bases.sum(-1, keepdim=True)
    p = g.combine(bases)
    mean = bases.mean(1); mean = mean / mean.sum(-1, keepdim=True)
    assert torch.allclose(p, mean, atol=1e-5)


def test_conststack_smoke():
    from microtwin.evaluate import fit_predict_conststack
    Z, P = _toy(n=20, taxa=6)
    pred = fit_predict_conststack(Z[:16], P[:16], Z[16:], inner=2, seed=0)
    assert pred.shape == (4, 6)
    assert np.allclose(pred.sum(1), 1, atol=1e-5)


def test_cnode2_smoke():
    from microtwin.evaluate import fit_predict
    Z, P = _toy(n=20, taxa=6)
    pred = fit_predict("cnode2", Z[:16], P[:16], Z[16:], seed=0)
    assert pred.shape == (4, 6)
    assert np.allclose(pred.sum(1), 1, atol=1e-4)
    assert (pred[Z[16:] == 0] == 0).all()


def test_lgbm_smoke():
    from microtwin.evaluate import fit_predict
    Z, P = _toy(n=20, taxa=6)
    pred = fit_predict("lgbm", Z[:16], P[:16], Z[16:], seed=0)
    assert pred.shape == (4, 6)
    assert np.allclose(pred.sum(1), 1, atol=1e-5)
    assert (pred[Z[16:] == 0] == 0).all()
