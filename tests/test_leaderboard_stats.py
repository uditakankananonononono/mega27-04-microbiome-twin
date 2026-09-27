import pytest
from microtwin.leaderboard_stats import compare_by_study


def test_sample_imbalanced_studies_get_equal_study_weight():
    r = compare_by_study([.1]*100+[.7], [.2]*100+[.2], ['big']*100+['small'], n_boot=0)
    assert r["delta_candidate_minus_baseline"] == pytest.approx(.2)
    assert r["verdict"] == "interval_disabled"


def test_one_study_cannot_claim_external_win():
    r = compare_by_study([.1,.1], [.2,.2], ['only','only'])
    assert r["verdict"] == "insufficient_studies"
    assert r["ci95_study_bootstrap"] is None


def test_two_studies_consistent_beat():
    r = compare_by_study([.1,.1,.1,.1], [.3,.3,.2,.2], ['a','a','b','b'],seed=1)
    assert r["verdict"] == "candidate_lower_interval"
    assert r["ci95_study_bootstrap"][1] < 0


def test_bad_alignment_rejected():
    with pytest.raises(ValueError):
        compare_by_study([.1], [.2], [])


def test_invalid_study_ids_fail_closed_instead_of_inflating_independent_studies():
    for bad in (None, "", "  ", float("nan"), float("inf")):
        with pytest.raises(ValueError, match="study ID"):
            compare_by_study([.1, .2], [.2, .3], ["valid", bad])
    r = compare_by_study([.1, .1], [.2, .2], [1, "1"])
    assert r["n_studies"] == 1
    assert r["verdict"] == "insufficient_studies"


def test_bootstrap_count_rejects_boolean():
    with pytest.raises(ValueError, match="n_boot"):
        compare_by_study([.1], [.2], ["one"], n_boot=True)


def test_whitespace_variant_is_one_study():
    r = compare_by_study([.1, .1], [.2, .2], ['study', ' study '])
    assert r['n_studies'] == 1
    assert r['verdict'] == 'insufficient_studies'


def test_favorable_synthetic_interval_is_not_external_win():
    r=compare_by_study([.1,.1],[.9,.8],["one","two"],n_boot=200,seed=1)
    assert r["verdict"]=="candidate_lower_interval"
    assert r["external_win_certified"] is False
    assert r["eligibility_status"]=="unverified"
    assert "comparator selection" in r["claim_gate_note"]
