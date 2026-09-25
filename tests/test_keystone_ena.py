import json, sys
sys.path.insert(0, "scripts")
from keystone_ena import pick_taxid, parse_count


def test_parsers():
    recs = [{"taxId": "1", "rank": "genus", "lineage": "Eukaryota; x"}, {"taxId": "538", "rank": "genus", "lineage": "Bacteria; Pseudomonadota; "}]
    assert pick_taxid(recs) == 538 and pick_taxid([]) is None
    assert parse_count("count\n42\n") == 42 and parse_count("error") is None and parse_count(None) is None


def test_committed_result():
    J = json.load(open("results/keystone_ena.json"))
    assert J["G1_pass"] and J["A1_pass"]
