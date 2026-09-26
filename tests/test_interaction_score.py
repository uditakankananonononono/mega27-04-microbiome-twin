import numpy as np
import pytest
from microtwin.interaction_score import heldout_scores


def test_positive_and_negative_scores_with_grouped_interval():
    out = heldout_scores([.2, .4, .2, .4], [.1, .2, .3, .6],
                         ids=["a", "b", "c", "d"], groups=[1, 1, 2, 2], seed=3)
    assert out["sample_scores"] == pytest.approx([.5, .5, -.5, -.5])
    assert out["ecosystem_score"] == pytest.approx(0)
    assert out["ci95"] == pytest.approx([-.5, .5])
    assert out["independent_groups"] == 2


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
