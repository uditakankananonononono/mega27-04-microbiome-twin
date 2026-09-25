import json
import numpy as np


def test_result_recorded_as_negative():
    J = json.load(open("results/keystone_igraph.json"))
    assert J["G1_pass"] and J["n_studies_solved"] >= 140
    assert J["I1_pass"] == (J["coef_GAI"] > 0 and J["p_GAI"] < 0.05)


def test_betweenness_star_graph():
    import igraph as ig
    g = ig.Graph(n=4, edges=[(0, 1), (0, 2), (0, 3)])
    bc = np.array(g.betweenness(directed=False))
    assert bc[0] == 3 and (bc[1:] == 0).all()
