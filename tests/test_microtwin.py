import numpy as np
import torch

from microtwin.data import CNODE_PUBLISHED_MEDIAN_BC, DATASETS, bray_curtis, load, preprocess
from microtwin.evaluate import kfold_indices, paired_bootstrap
from microtwin.models import CNODE, GLVSteady, GraphTwin, PresenceMean, bc_loss, predict_torch, train_torch


def test_bray_curtis_bounds():
    p = np.array([[0.5, 0.5, 0.0]]); q = np.array([[0.0, 0.0, 1.0]])
    assert np.isclose(bray_curtis(p, p)[0], 0.0)
    assert np.isclose(bray_curtis(p, q)[0], 1.0)


def test_preprocess_dedups_and_normalizes():
    P = np.array([[1, 2, 0, 3], [1, 0, 0, 0], [0, 5, 0, 1]], float)  # taxa x samples
    Z, Pn = preprocess(P)
    assert Z.shape == Pn.shape
    assert np.allclose(Pn.sum(1), 1) and np.allclose(Z.sum(1), 1)
    assert len({tuple(z > 0) for z in Z}) == len(Z)


def test_all_real_datasets_load():
    for d in DATASETS:
        Z, P = load(d)
        assert len(Z) >= 20 and np.all((P > 0) <= (Z > 0))
    assert set(CNODE_PUBLISHED_MEDIAN_BC) == set(DATASETS)


def _toy():
    rng = np.random.default_rng(0)
    Zb = (rng.random((40, 6)) < 0.6).astype(float); Zb[Zb.sum(1) == 0, 0] = 1
    P = Zb * rng.random(6); P /= P.sum(1, keepdims=True)
    return Zb / Zb.sum(1, keepdims=True), P


def test_models_respect_simplex_and_absence():
    Z, _ = _toy()
    for m in [CNODE(6), GLVSteady(6), GraphTwin(6, prior=np.ones(6) / 6)]:
        q = predict_torch(m.eval(), Z)
        assert np.allclose(q.sum(1), 1, atol=1e-5)
        assert np.all(q[Z == 0] == 0)


def test_cnode_zero_init_is_identity():
    Z, _ = _toy()
    assert np.allclose(predict_torch(CNODE(6), Z), Z, atol=1e-6)


def test_training_reduces_loss():
    Z, P = _toy()
    m = GLVSteady(6)
    before = bc_loss(m(torch.tensor(Z, dtype=torch.float32)), torch.tensor(P, dtype=torch.float32)).item()
    train_torch(m, Z, P, epochs=60, lr=0.05)
    after = bc_loss(m(torch.tensor(Z, dtype=torch.float32)), torch.tensor(P, dtype=torch.float32)).item()
    assert after < before


def test_presence_mean_null():
    Z, P = _toy()
    q = PresenceMean().fit(Z, P).predict(Z)
    assert np.allclose(q.sum(1), 1) and np.all(q[Z == 0] == 0)


def test_kfold_partition():
    folds = kfold_indices(23, 5)
    assert sorted(np.concatenate(folds).tolist()) == list(range(23))


def test_paired_bootstrap_sign():
    a = np.full(50, 0.1); b = np.full(50, 0.2)
    est, lo, hi = paired_bootstrap(a, b, n_boot=100)
    assert est < 0 and hi < 0


def test_popforecast_conditional_ignores_zeros():
    from microtwin.popforecast import forecast
    days = np.array([0.0, 1.0, 2.0])
    train = [(days, np.array([1e6, 0.0, 1e6])), (days, np.array([1e6, 1e6, 1e6]))]
    p = forecast(train, days, 1e6, tau=0, eps=1e3, conditional=True)
    assert np.allclose(p, 6.0, atol=1e-6)
    pu = forecast(train, days, 1e6, tau=0, eps=1e3, conditional=False)
    assert pu[1] < 6.0


def test_popforecast_offset_decays():
    from microtwin.popforecast import forecast
    days = np.array([0.0, 5.0, 50.0])
    train = [(days, np.full(3, 1e6))]
    p = forecast(train, days, 1e8, tau=5.0, eps=0.0)
    assert np.isclose(p[0], 8.0) and p[1] < p[0] and abs(p[2] - 6.0) < 1e-3
