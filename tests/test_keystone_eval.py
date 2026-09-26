import pytest
from microtwin.keystone_eval import prospective_precision_at_k


def test_groups_rank_separately():
    r=prospective_precision_at_k([.9,.1,.1,.9],[.8,0,0,0],['A','A','B','B'],k=1,effect_cutoff=.5)
    assert r['n_experiments']==2 and r['macro_precision_at_k']==pytest.approx(.5)


def test_missing_group_rejected():
    with pytest.raises(ValueError):prospective_precision_at_k([.1],[1],[''],k=1)
