import json, pandas as pd
def test_traits_outputs():
    R = pd.read_csv("results/keystone_traits_tests.csv"); assert set(["anaerobe", "genome_size"]) <= set(R.trait)
    assert ((R.q_spearman >= R.p_spearman - 1e-12) & (R.q_spearman <= 1)).all()
    c = json.load(open("results/keystone_traits_confound.json")); assert 0 < c["strat_perm_p"] <= 1
