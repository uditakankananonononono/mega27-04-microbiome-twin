import json, sys
import pandas as pd
sys.path.insert(0, "scripts")
from keystone_protraits import genus_share, COL


def test_genus_share_coding():
    df = pd.DataFrame({"Organism_name": ["Bacteroides fragilis", "bacteroides ovatus", "Escherichia coli", "Candidatus Foo bar", "[Clostridium] x", "Yersinia pestis"],
                       COL: ["1", "0", "0", "1", "1", "?"]})
    g = genus_share(df)
    assert g.loc["Bacteroides", "pt_anaerobe"] == 0.5 and g.loc["Bacteroides", "n_org"] == 2
    assert "Candidatus" not in g.index and "[clostridium]" not in g.index and "Yersinia" not in g.index


def test_committed_result_gate_failed():
    J = json.load(open("results/keystone_protraits.json"))
    assert J["G1_pass"] is False and J["H1_pass"] is False and J["n_genera"] == 51
