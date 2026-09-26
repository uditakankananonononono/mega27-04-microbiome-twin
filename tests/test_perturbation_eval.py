import pytest
from microtwin.perturbation_eval import direction_accuracy


def test_zero_predictions_abstain_and_small_observed_changes_excluded():
    r=direction_accuracy([1,0,-1,1],[1,-1,1,.01],groups=['A','A','B','B'],threshold=.1)
    assert r['eligible']==3 and r['attempted']==2
    assert r['accuracy']==pytest.approx(.5) and r['coverage']==pytest.approx(2/3)


def test_no_scored_direction_is_unavailable():
    r=direction_accuracy([0],[1],groups=['experiment'])
    assert r['accuracy'] is None and r['status']=='unavailable_no_scored_directions'


def test_group_labels_required():
    with pytest.raises(ValueError):direction_accuracy([1],[1],groups=[''])


def test_missing_and_equivalent_group_ids_do_not_inflate_experiments():
    for bad in (None, "", "  ", float("nan"), float("inf")):
        with pytest.raises(ValueError, match="group required"):
            direction_accuracy([1, 1], [1, 1], groups=["valid", bad])
    r = direction_accuracy([1, 1], [1, 1], groups=[1, "1"])
    assert r["independent_experiment_groups"] == 1
    assert "not proof" in r["note"]
