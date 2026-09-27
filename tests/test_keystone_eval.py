import pytest
from microtwin.keystone_eval import prospective_precision_at_k


def test_groups_rank_separately():
    r=prospective_precision_at_k([.9,.1,.1,.9],[.8,0,0,0],['A','A','B','B'],k=1,effect_cutoff=.5)
    assert r['n_experiments']==2 and r['macro_precision_at_k']==pytest.approx(.5)


def test_missing_group_rejected():
    with pytest.raises(ValueError):prospective_precision_at_k([.1],[1],[''],k=1)


def test_missing_or_equivalent_group_ids_do_not_inflate_experiments():
    for bad in (None, '', ' ', float('nan'), float('inf')):
        with pytest.raises(ValueError, match='group required'):
            prospective_precision_at_k([.1, .2], [1, 1], ['valid', bad])
    r=prospective_precision_at_k([.9,.1], [1,0], ['study', ' study '], k=1)
    assert r['n_experiments']==1
    with pytest.raises(ValueError, match='positive integer'):
        prospective_precision_at_k([.1], [1], ['study'], k=True)
