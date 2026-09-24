import json, pandas as pd
def test_gtdb_replication_file():
    d = json.load(open("results/keystone_gtdb.json"))
    assert d["n_mapped"] <= d["n_total"]
    R = pd.read_csv("results/keystone_gtdb_phylum_enrichment.csv")
    assert (R.q_bh >= R.p - 1e-12).all() and R.top25.sum() == 25
