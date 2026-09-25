import json, sys
import numpy as np, pandas as pd
sys.path.insert(0, "scripts")
from keystone_uniprot import ugai


def test_ugai():
    d = pd.DataFrame({"n_pfor": [2, 0, 1], "n_cox": [0, 3, 1], "n_recA": [1, 2, 0]})
    u = ugai(d)
    assert u[0] == 1.0 and u[1] == -1.0 and np.isnan(u[2])


def test_committed_result():
    J = json.load(open("results/keystone_uniprot.json"))
    assert J["G1_pass"] and J["U1_pass"] and J["spearman_UGAI_vs_KEGG_GAI"] >= 0.6
