import json
import pandas as pd


def test_cache_and_result():
    C = pd.read_csv("results/keystone_rnacentral_counts.csv")
    assert C.rrna_seqs.notna().sum() >= 180 and (C.rrna_seqs.dropna() >= 0).all()
    J = json.load(open("results/keystone_rnacentral.json"))
    assert J["G1_pass"] and J["R1_pass"] == (J["slope_GAI"] > 0 and J["p_GAI_HC3"] < 0.05)


def test_api_url():
    import sys
    sys.path.insert(0, "scripts")
    import keystone_rnacentral as k
    assert "/rnacentral?" in k.API and k.API.endswith("query=")
