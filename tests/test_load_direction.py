import pytest
from microtwin.load_direction import bound_absolute_fold


def bound(q,**kwargs):
    return bound_absolute_fold([.1,.1],[.2,.2],q,measurement_compatible=kwargs.pop('measurement_compatible',True),**kwargs)


def test_relative_double_both_absolute_signs_feasible():
    result=bound([.25,4])
    assert result['absolute_fold_bounds']==[.5,8]
    assert result['status']=='opposite_direction_feasibility_witness'
    assert [x['absolute_fold'] for x in result['witnesses']]==[.5,8]
    assert not result['causal_interpretation']


def test_tight_load_changes_conclusion():
    r=bound([.9,1.1]);assert r['absolute_fold_bounds']==[1.8,2.2] and r['status']=='increase_under_supplied_box'


@pytest.mark.parametrize('q',[[.5,1],[.5,.5]])
def test_boundary_is_not_strict_sign(q):
    assert bound(q)['status']=='abstain'


def test_unknown_load_and_unverified_measurement():
    assert bound(None)['absolute_fold_bounds'] is None
    assert bound([.9,1.1],measurement_compatible=False)['status']=='abstain'


@pytest.mark.parametrize('q',[[0,1],[-1,1],[2,1],[float('nan'),1],[1,float('inf')],[True,1]])
def test_invalid_load(q):
    with pytest.raises(ValueError):bound(q)


@pytest.mark.parametrize('p',[[0,.1],[.1,2],[.2,.1]])
def test_invalid_or_zero_fraction(p):
    with pytest.raises(ValueError):bound_absolute_fold(p,[.2,.2],[1,1],measurement_compatible=True)


def test_frozen_grid_all_cells_and_negative_scope():
    import importlib.util
    spec=importlib.util.spec_from_file_location('grid','scripts/load_direction_grid.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    r=m.run();assert r['cell_count']==11 and r['useful_win'] is False
    assert max(c['corner_verification_max_error'] for c in r['cells'])<=1e-12
    assert {c['status'] for c in r['cells']}=={'increase_under_supplied_box','decrease_under_supplied_box','opposite_direction_feasibility_witness','abstain'}
