import json
import pandas as pd


def test_result_consistent():
    J = json.load(open("results/keystone_methodgeneral.json"))
    ok = all(J[k]["coef_oral"] > 0 and J[k]["p_oral"] < 0.05 for k in ["gglasso", "igraph"])
    assert J["MG1_pass"] == ok and J["gglasso"]["n_studies"] >= 140


def test_truthy():
    import sys
    sys.path.insert(0, "scripts")
    import keystone_methodgeneral as k
    assert k.truthy(pd.Series([True, "False", "true", 1, 0.0])).tolist() == [1, 0, 1, 1, 0]
