import pytest
from microtwin.perturbation_eval import direction_accuracy


def test_zero_predictions_abstain_and_small_observed_changes_excluded():
    r=direction_accuracy([1,0,-1,1],[1,-1,1,.01],groups=['A','A','B','B'],threshold=.1)
    assert r['eligible']==3 and r['attempted']==2
    assert r['accuracy']==pytest.approx(.5) and r['coverage']==pytest.approx(2/3)


def test_no_scored_direction_is_unavailable():
    r=direction_accuracy([0],[1],groups=['experiment'])
    assert r['accuracy'] is None and r['status']=='unavailable_no_scored_directions'
    assert r['submitted_groups']==0 and not r['intervention_validated']


def test_group_labels_required():
    with pytest.raises(ValueError):direction_accuracy([1],[1],groups=[''])


def test_missing_and_equivalent_group_ids_do_not_inflate_experiments():
    for bad in (None, "", "  ", float("nan"), float("inf")):
        with pytest.raises(ValueError, match="group required"):
            direction_accuracy([1, 1], [1, 1], groups=["valid", bad])
    r = direction_accuracy([1, 1], [1, 1], groups=[1, "1"])
    assert r["submitted_groups"] == 1
    assert not r["experiment_independence_verified"] and not r["intervention_validated"]


def test_group_macro_differs_from_taxon_pooled_on_imbalanced_groups():
    r=direction_accuracy([1]*11,[1]*10+[-1],groups=['large']*10+['small'],seed=7,n_boot=200)
    assert r['accuracy']==pytest.approx(10/11)
    assert r['group_macro_accuracy']==pytest.approx(.5)
    assert r['group_bootstrap_95ci']==pytest.approx([0,1])
    assert r['submitted_groups']==2
    assert sum(x['attempted'] for x in r['attempted_group_summaries'])==11
    assert 'large' not in str(r['attempted_group_summaries'])
    assert direction_accuracy([1]*11,[1]*10+[-1],groups=['large']*10+['small'],seed=7,n_boot=200)['group_bootstrap_95ci']==r['group_bootstrap_95ci']


def test_single_attempted_group_has_no_interval_and_threshold_edge_excluded():
    r=direction_accuracy([1,1,0],[1,.1,1],groups=['a','b','b'],threshold=.1)
    assert r['eligible']==2 and r['attempted']==1
    assert r['group_macro_accuracy']==1 and r['group_bootstrap_95ci'] is None
    assert r['submitted_groups']==1


@pytest.mark.parametrize('n_boot,seed',[(0,0),(10001,0),(True,0),(10,-1),(10,1.2)])
def test_bad_bootstrap_controls_rejected(n_boot,seed):
    with pytest.raises(ValueError,match='n_boot'):
        direction_accuracy([1],[1],groups=['a'],n_boot=n_boot,seed=seed)


def test_perfect_synthetic_direction_is_not_validated_intervention():
    r=direction_accuracy([1,1],[1,1],groups=["a","b"],n_boot=10)
    assert r["accuracy"]==r["group_macro_accuracy"]==1
    assert r["submitted_groups"]==2
    assert not r["experiment_independence_verified"] and not r["intervention_validated"]
