import json, sys
sys.path.insert(0, "scripts")
from keystone_gbif import accept


def test_accept():
    assert accept({"matchType": "EXACT", "rank": "GENUS", "kingdom": "Bacteria"})
    assert not accept({"matchType": "FUZZY", "rank": "GENUS", "kingdom": "Bacteria"})
    assert not accept({"matchType": "EXACT", "rank": "GENUS", "kingdom": "Plantae"}) and not accept(None)


def test_committed_result():
    J = json.load(open("results/keystone_gbif.json"))
    assert J["G1_pass"] and J["B1_pass"] and not J["rival_G_supported"]
