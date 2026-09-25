import json
import numpy as np, pandas as pd


def test_cache_and_result():
    C = pd.read_csv("results/keystone_interpro_counts.csv")
    assert C[["n_pfor", "n_cox", "n_recA"]].notna().all().all()
    J = json.load(open("results/keystone_interpro.json"))
    assert J["G1_pass"] and J["P1_pass"] == (J["ols"]["slope_IGAI"] > 0 and J["ols"]["p_HC3"] < 0.05)


def test_igai_bounds():
    import sys
    sys.path.insert(0, "scripts")
    import keystone_interpro as k
    d = pd.DataFrame({"n_pfor": [5, 0, 1], "n_cox": [0, 4, 1], "n_recA": [2, 2, 0]})
    v = k.igai(d)
    assert v[0] == 1 and v[1] == -1 and np.isnan(v[2])
