import json, sys
sys.path.insert(0, "scripts")
from keystone_disbiome import genus_counts


def test_genus_counts():
    recs = [{"experiment_id": 1, "publication_id": 10, "organism_name": "Bacteroides fragilis"},
            {"experiment_id": 2, "publication_id": 10, "organism_name": "bacteroides"},
            {"experiment_id": 2, "publication_id": 10, "organism_name": "Bacteroides ovatus"},
            {"experiment_id": 3, "publication_id": 11, "organism_name": "uncultured Bacteroides"},
            {"experiment_id": 4, "publication_id": 12, "organism_name": None}]
    c = genus_counts(recs)
    assert c.loc["Bacteroides", "n_exp"] == 2 and c.loc["Bacteroides", "n_pub"] == 1 and len(c) == 1


def test_committed_result():
    J = json.load(open("results/keystone_disbiome.json"))
    assert J["G1_pass"] and J["D1_pass"] and J["ml"]["p_kscore"] < 0.05
