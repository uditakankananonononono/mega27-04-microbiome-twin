import json
def test_kegg_outputs():
    d = json.load(open("results/keystone_kegg.json"))
    assert d["n_genera_mapped"] <= d["n_genera"] and "GAI" in d["fe_logit_GAI"]["coef"]
    assert -1 <= d["vs_madin_anaerobe"]["GAI"][0] <= 1
def test_bvbrc_outputs():
    d = json.load(open("results/keystone_bvbrc.json")); assert d["n_genera_bvbrc"] > 0 and "bv_anaerobe" in d["fe_logit"]["coef"]
