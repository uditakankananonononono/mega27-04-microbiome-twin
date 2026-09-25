import sys, math
sys.path.insert(0, "scripts")
from keystone_genomesize import genus_stats

def test_genus_stats():
    rep = {"reports": [{"assembly_stats": {"total_sequence_length": "2000000", "gc_percent": 40}},
                       {"assembly_stats": {"total_sequence_length": "4000000", "gc_percent": 50}}]}
    assert genus_stats(rep) == (3.0, 45.0, 2)
    L, G, n = genus_stats({}); assert math.isnan(L) and n == 0
