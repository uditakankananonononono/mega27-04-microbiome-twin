import sys, pandas as pd
sys.path.insert(0, "scripts")
from keystone_ijsem import genus_anaerobe

def test_genus_anaerobe_coding():
    df = pd.DataFrame({"Genus name": ["bacteroides", "Bacteroides", "Escherichia", "X"], "oxygen preference": ["anaerobic", "facultative anaerobe", "aerobic", None]})
    g = genus_anaerobe(df)
    assert g.loc["Bacteroides", "ijsem_anaerobe"] == 0.5 and g.loc["Bacteroides", "n_records"] == 2
    assert g.loc["Escherichia", "ijsem_anaerobe"] == 0 and "X" not in g.index
