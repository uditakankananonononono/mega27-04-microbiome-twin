from scripts.hmp_v13_intake import lineage


def test_lineage_only_named_genus_and_parents():
    genus, parents = lineage('Root;p__Bacteroidetes;c__C;o__O;f__F;g__Bacteroides')
    assert genus == 'Bacteroides'
    assert parents[-1] == 'f__F'
    assert lineage('Root;p__Bacteroidetes;g__')[0] is None
    assert lineage('Root;p__Bacteroidetes;g__unclassified')[0] is None
