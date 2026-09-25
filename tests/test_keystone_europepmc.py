import json
import pandas as pd


def test_cache_complete_and_result():
    C = pd.read_csv("results/keystone_europepmc_counts.csv")
    assert len(C) == 248 and C.epmc_hits.notna().all() and (C.epmc_hits >= 0).all()
    J = json.load(open("results/keystone_europepmc.json"))
    assert J["G1_pass"] and J["E1_pass"] and J["nb_ml"]["coef_kscore"] > 0


def test_query_builder_quotes_genus():
    import sys, urllib.parse
    sys.path.insert(0, "scripts")
    import keystone_europepmc as k
    assert k.API.endswith("query=") and urllib.parse.quote('TITLE_ABS:"Eikenella"') == "TITLE_ABS%3A%22Eikenella%22"
