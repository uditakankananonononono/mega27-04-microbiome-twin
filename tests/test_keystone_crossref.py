import json
import pandas as pd


def test_cache_complete_and_result():
    C = pd.read_csv("results/keystone_crossref_counts.csv")
    assert len(C) == 248 and C.cr_works.notna().all() and (C.cr_works >= 0).all()
    J = json.load(open("results/keystone_crossref.json"))
    assert J["G1_pass"] and J["O1_pass"] and J["O1_disbiome"]["coef_kscore"] > 0


def test_query_url():
    import sys, urllib.parse
    sys.path.insert(0, "scripts")
    import keystone_crossref as k
    assert k.API.startswith("https://api.crossref.org/works?rows=0") and k.API.endswith("query.bibliographic=")
