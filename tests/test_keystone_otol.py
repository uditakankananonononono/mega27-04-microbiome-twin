import json, sys
import numpy as np
sys.path.insert(0, "scripts")
from keystone_otol import parse_newick, grafen_cov


def test_parse_and_grafen():
    parent, label = parse_newick("((ott1,ott2)n1,ott3)root;")
    tips = [label.index(t) for t in ("ott1", "ott2", "ott3")]
    V = grafen_cov(parent, tips)
    # root has 3 tips -> height 1; n1 has 2 tips -> height 0.5
    assert np.allclose(np.diag(V), 1.0) and np.isclose(V[0, 1], 0.5) and np.isclose(V[0, 2], 0.0)


def test_committed_result():
    J = json.load(open("results/keystone_otol.json"))
    assert J["G1_pass"] and J["H1_pass"] and J["brownian"]["p"] < 0.05 and J["n_on_tree"] >= 150
