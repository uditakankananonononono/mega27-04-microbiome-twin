import numpy as np
import pytest
from microtwin.interaction_score import heldout_scores


def test_positive_and_negative_scores_with_grouped_interval():
    out = heldout_scores([.2, .4, .2, .4], [.1, .2, .3, .6],
                         ids=["a", "b", "c", "d"], groups=[1, 1, 2, 2], seed=3)
    assert out["sample_scores"] == pytest.approx([.5, .5, -.5, -.5])
    assert out["ecosystem_score"] == pytest.approx(0)
    assert out["ci95"] == pytest.approx([-.5, .5])
    assert out["submitted_groups"] == 2


def test_zero_prior_cannot_be_sold_as_interaction_gain():
    out = heldout_scores([0, .2], [.1, .1], n_boot=0)
    assert out["sample_scores"] == [None, .5]
    assert out["n_zero_prior_error"] == 1
    assert heldout_scores([0], [0])["status"] == "unavailable_no_positive_prior_error"


def test_invalid_or_unpaired_errors_rejected():
    for prior, other in [([.2], [.2, .3]), ([-.1], [.2]), ([np.nan], [.2])]:
        with pytest.raises(ValueError):
            heldout_scores(prior, other)
    with pytest.raises(ValueError):
        heldout_scores([.1, .2], [.1, .2], ids=["same", "same"])


def test_dependence_cli_reads_only_paired_heldout_errors(tmp_path, capsys):
    import json
    import pandas as pd
    from microtwin.cli import main
    f = tmp_path / "paired.csv"
    pd.DataFrame({"sample_id": ["a", "b"], "study": ["S1", "S2"],
                  "prior_error": [.4, .2], "interaction_error": [.2, .3]}).to_csv(f, index=False)
    assert main(["dependence", str(f), "--n-boot", "0"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "heldout_predictive_score"
    assert out["sample_scores"] == pytest.approx([.5, -.5])
    assert out["ci95"] is None


def test_single_study_does_not_get_false_interval():
    out = heldout_scores([.2, .3], [.1, .2], groups=["one", "one"])
    assert out["ci95"] is None
    assert out["interval_status"] == "insufficient_submitted_groups"


def test_missing_or_normalized_duplicate_identifiers_fail_closed():
    for group in [None, "", "  ", float("nan"), float("inf")]:
        with pytest.raises(ValueError):
            heldout_scores([.2], [.1], groups=[group])
    for sample_id in [None, "", "  ", float("nan"), float("inf")]:
        with pytest.raises(ValueError):
            heldout_scores([.2], [.1], ids=[sample_id])
    with pytest.raises(ValueError):
        heldout_scores([.2, .3], [.1, .2], ids=[1, "1"])
    out = heldout_scores([.2, .3], [.1, .2], groups=[1, "1"])
    assert out["submitted_groups"] == 1
    assert out["ci95"] is None


def test_cli_nan_study_label_is_not_counted_as_independent(tmp_path):
    import pandas as pd
    from microtwin.cli import main
    f = tmp_path / "paired.csv"
    pd.DataFrame({"sample_id": ["a", "b"], "study": ["S1", None],
                  "prior_error": [.4, .2], "interaction_error": [.2, .3]}).to_csv(f, index=False)
    with pytest.raises(SystemExit, match="group ids must be nonempty"):
        main(["dependence", str(f)])


def test_whitespace_variant_group_is_one_independent_unit():
    with pytest.raises(ValueError, match='unique'):
        heldout_scores([.2,.2], [.1,.1], ids=['a',' a '])
    r=heldout_scores([.2,.2], [.1,.1], groups=['study',' study '])
    assert r['submitted_groups']==1
    assert r['ci95'] is None


def test_ungrouped_multiple_samples_do_not_get_independence_interval():
    r=heldout_scores([.2,.3],[.1,.2],ids=["a","b"])
    assert r["ecosystem_score"] is not None
    assert r["ci95"] is None and r["interval_status"]=="unavailable_no_groups"
    assert r["submitted_groups"]==0 and not r["group_independence_verified"]
