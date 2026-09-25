import json
import pandas as pd


def test_bambi_result():
    J = json.load(open("results/keystone_bambi.json"))
    assert J["BY1_pass"] == all(J[k]["P_oral_gt0"] >= 0.975 for k in ["gglasso", "igraph"])
    assert all(J[k]["max_rhat"] < 1.05 for k in ["gglasso", "igraph"])


def test_pubtator_result_and_cache():
    C = pd.read_csv("results/keystone_pubtator_counts.csv")
    assert C[["n_all", "n_oral"]].notna().all().all() and (C.n_oral <= C.n_all).all()
    J = json.load(open("results/keystone_pubtator.json"))
    ok = J["G1_pass"] and all(J[k]["coef_OLF_z"] > 0 and J[k]["p_OLF_z"] < 0.05 for k in ["gglasso", "igraph"])
    assert J["PT1_pass"] == ok
