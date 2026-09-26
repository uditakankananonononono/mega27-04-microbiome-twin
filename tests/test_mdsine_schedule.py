import numpy as np
import pytest
from microtwin.mdsine_schedule import scheduled_days


def test_scheduled_days_discard_first_two_without_abundance():
    np.testing.assert_allclose(scheduled_days([2., 0., 1., 0.5, 1.5], 3), [1., 1.5, 2.])


def test_scheduled_days_reject_ambiguous_schedule():
    with pytest.raises(ValueError, match='length'): scheduled_days([0., 0.5, 1.], 2)
    with pytest.raises(ValueError, match='unique'): scheduled_days([1., 1.], 2)
