import json
import pandas as pd


def test_cache_and_result():
    C = pd.read_csv("results/keystone_ensembl_counts.csv")
    assert C.ensembl_genomes.notna().sum() >= 180 and (C.ensembl_genomes.dropna() >= 0).all()
    J = json.load(open("results/keystone_ensembl.json"))
    assert J["G1_pass"] and J["S1_pass"] == (J["slope_GAI"] > 0 and J["p_GAI_HC3"] < 0.05)


def test_api_url():
    import sys
    sys.path.insert(0, "scripts")
    import keystone_ensembl as k
    assert "ensemblGenomes_genome" in k.API and k.API.endswith("query=")
