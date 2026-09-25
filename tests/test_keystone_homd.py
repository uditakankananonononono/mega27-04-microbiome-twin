import json
import pandas as pd


def test_result_consistent():
    J = json.load(open("results/keystone_homd.json"))
    assert J["G1_pass"] and J["site_column"] == "Body Site(s)"
    assert J["M1_pass"] == (J["slope_GAI"] > 0 and J["p_GAI_HC3"] < 0.05)


def test_oral_filter():
    import sys
    sys.path.insert(0, "scripts")
    import keystone_homd as k
    T = pd.DataFrame({"Genus": ["A", "B", "C"], "Body Site(s)": ["Oral (Abundance: High)", "Nasal", "Skin | oral"]})
    og, g, s = k.oral_genera(T)
    assert og == {"A", "C"} and g == "Genus" and s == "Body Site(s)"
