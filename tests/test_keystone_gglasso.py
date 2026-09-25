import json, sys
import numpy as np, pandas as pd
sys.path.insert(0, "scripts")
from keystone_gglasso import pcor_degree, clr_corr


def test_pcor_degree_and_clr():
    T = np.array([[2.0, -1.0, 0.0], [-1.0, 2.0, 0.0], [0.0, 0.0, 1.0]])
    d = pcor_degree(T)
    assert np.allclose(d, [0.5, 0.5, 0.0])
    X = pd.DataFrame([[1, 2, 3], [3, 1, 0], [0, 5, 2], [4, 4, 4]], columns=list("abc"))
    S, n, keep = clr_corr(X)
    assert n == 4 and keep.sum() == 3 and np.allclose(np.diag(S), 1)


def test_committed_result_failed():
    J = json.load(open("results/keystone_gglasso.json"))
    assert J["G1_pass"] and J["H1_pass"] is False and J["n_studies_solved"] == 160
