import json, sys
sys.path.insert(0, "scripts")
from keystone_wikidata import gram_table, NEG, POS


def test_gram_table():
    b = lambda n, q: {"name": {"value": n}, "g": {"value": "http://www.wikidata.org/entity/" + q}}
    g = gram_table([b("Escherichia", NEG), b("Bacillus", POS), b("Mixed", NEG), b("Mixed", POS), b("Other", "Q1")])
    assert g["Escherichia"] == 1 and g["Bacillus"] == 0 and "Mixed" not in g.index and "Other" not in g.index
    assert POS == "Q857288"


def test_committed_result():
    J = json.load(open("results/keystone_wikidata.json"))
    assert J["G1_pass"] and J["W0_verdict"] == "replicated"
