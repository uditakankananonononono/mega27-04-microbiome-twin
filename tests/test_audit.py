import numpy as np
from microtwin.audit import audit, fit_prior, predict_prior, fit_interaction, predict_interaction, bray_curtis


def _synthetic(n=80, N=12, seed=0, interact=True):
    rng = np.random.default_rng(seed)
    Z = rng.random((n, N)) < 0.6; Z[:, 0] = True
    W = np.zeros((N, N)); W[1, 2] = 2.5 if interact else 0.0
    mu = rng.normal(0, 1, N)
    L = mu + Z @ W.T + 0.05 * rng.normal(size=(n, N))
    P = np.where(Z, np.exp(L), 0); return P / P.sum(1, keepdims=True)


def test_prediction_on_simplex_and_masked():
    P = _synthetic(); Z = P > 0
    for pred in (predict_prior(fit_prior(P), Z), predict_interaction(fit_interaction(P, 10.0), Z)):
        assert np.allclose(pred.sum(1), 1) and np.all(pred[~Z] == 0)


def test_interaction_model_detects_planted_interaction():
    r = audit(_synthetic(interact=True), k=5)
    assert r["median_interaction"] < r["median_prior"] and r["wilcoxon_p"] < 0.01


def test_no_gain_without_interactions():
    r = audit(_synthetic(interact=False), k=5)
    assert r["median_interaction"] >= r["median_prior"] - 0.01


def test_bray_curtis_identity():
    p = np.array([[0.5, 0.5, 0]]); assert bray_curtis(p, p)[0] == 0


def test_cli_audit_runs_on_table(tmp_path, capsys):
    import pandas as pd
    from microtwin.cli import main
    P = _synthetic(interact=True)
    f = tmp_path / "t.tsv"; pd.DataFrame(P.T, index=[f"g{i}" for i in range(P.shape[1])]).to_csv(f, sep="\t")
    assert main(["audit", str(f), "--k", "4"]) == 0
    assert "interactions add predictive value" in capsys.readouterr().out
