import copy
import pytest
from microtwin.multimodel_leaderboard import freeze_comparator, compare_frozen_models


def selection():
    return freeze_comparator({'twin':[.4,.4], 'prior':[.2,.2], 'cnode':[.3,.3]},['v1','v2'], candidate='twin')


def test_validation_only_comparator():
    s=selection()
    r=compare_frozen_models(s,{'twin':[.1]*8,'prior':[.4]*8,'cnode':[.05]*8},[f't{i}' for i in range(8)])
    assert r['selected_comparator']=='prior' # not test-best cnode
    assert r['comparisons']['prior']['p_two_sided_exact_sign_flip']==2/256
    assert r['comparisons']['prior']['p_holm']==4/256
    assert r['comparisons']['cnode']['macro_delta_candidate_minus_baseline']>0
    assert not r['external_win_certified']


def test_family_weight_not_sample_weight():
    r=compare_frozen_models(selection(),{'twin':[.1]*100+[.9],'prior':[.3]*100+[.5],'cnode':[.2]*101},['t1']*100+['t2'])
    assert r['macro_family_median_losses']['twin']==.5
    assert r['comparisons']['prior']['macro_delta_candidate_minus_baseline']==pytest.approx(.1)


def test_ties_deterministic():
    s=freeze_comparator({'twin':[.3,.3],'z':[.2,.2],'a':[.2,.2]},['v1','v2'],candidate='twin')
    assert s['selected_comparator']=='a'


@pytest.mark.parametrize('change',['overlap','drop','tamper','missing','nan','few','many'])
def test_fail_closed(change):
    s=copy.deepcopy(selection()); errors={'twin':[.1,.2],'prior':[.3,.4],'cnode':[.2,.3]}; ids=['t1','t2']
    if change=='overlap':ids=['v1','t2']
    if change=='drop':errors.pop('cnode')
    if change=='tamper':s['selected_comparator']='cnode'
    if change=='missing':s.pop('candidate')
    if change=='nan':errors['twin'][0]=float('nan')
    if change=='few':ids=['t1','t1']
    if change=='many':ids=[f't{i}' for i in range(17)];errors={m:[.2]*17 for m in errors}
    with pytest.raises(ValueError):compare_frozen_models(s,errors,ids)


def test_zero_difference_p_one():
    r=compare_frozen_models(selection(),{m:[.2,.2] for m in ['twin','prior','cnode']},['t1','t2'])
    assert all(x['p_holm']==1 for x in r['comparisons'].values())


def test_primary_selected_interval_and_input_unchanged():
    s=selection(); before=copy.deepcopy(s)
    r=compare_frozen_models(s,{'twin':[.1,.1],'prior':[.3,.3],'cnode':[.2,.2]},['t1','t2'],n_boot=100)
    assert r['primary_selected_comparator_statistic']['ci95_study_bootstrap']==pytest.approx([-.2,-.2])
    assert s==before


@pytest.mark.parametrize('n_boot,seed',[(-1,0),(10001,0),(True,0),(100,-1),(100,True)])
def test_bootstrap_controls(n_boot,seed):
    with pytest.raises(ValueError):
        compare_frozen_models(selection(),{m:[.2,.2] for m in ['twin','prior','cnode']},['t1','t2'],n_boot=n_boot,seed=seed)
