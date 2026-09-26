import pytest
from microtwin.leaderboard_stats import compare_by_study


def test_sample_imbalanced_studies_get_equal_study_weight():
    r = compare_by_study([.1]*100+[.7], [.2]*100+[.2], ['big']*100+['small'], n_boot=0)
    assert r["delta_candidate_minus_baseline"] == pytest.approx(.2)
    assert r["verdict"] == "interval_disabled"


def test_one_study_cannot_claim_external_win():
    r = compare_by_study([.1,.1], [.2,.2], ['only','only'])
    assert r["verdict"] == "insufficient_independent_studies"
    assert r["ci95_study_bootstrap"] is None


def test_two_studies_consistent_beat():
    r = compare_by_study([.1,.1,.1,.1], [.3,.3,.2,.2], ['a','a','b','b'],seed=1)
    assert r["verdict"] == "WIN"
    assert r["ci95_study_bootstrap"][1] < 0


def test_bad_alignment_rejected():
    with pytest.raises(ValueError):
        compare_by_study([.1], [.2], [])
