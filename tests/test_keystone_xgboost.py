import json


def test_result_consistent():
    J = json.load(open("results/keystone_xgboost.json"))
    assert J["G1_pass"] and J["n_genera"] >= 180
    assert J["X1_pass"] == (J["delta_mean"] > 0 and J["n_positive"] >= 15)


def test_data_builder():
    import sys
    sys.path.insert(0, "scripts")
    import keystone_xgboost as k
    M = k.data()
    assert {"GAI", "lra", "log_ena", "frac_top"} <= set(M.columns) and M[["GAI", "lra", "log_ena"]].notna().all().all()
