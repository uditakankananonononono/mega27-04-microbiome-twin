import numpy as np
import pytest
from microtwin.neighborhood_twin import NeighborhoodTrustTwin


def test_mask_simplex_and_bounded_gate():
    m = NeighborhoodTrustTwin().fit([[1, 1, 0], [0, 1, 1]], [[.8, .2, 0], [0, .2, .8]])
    pred, d = m.predict_with_details([[1, 1, 0], [0, 1, 1], [0, 1, 0]])
    np.testing.assert_allclose(pred.sum(1), 1)
    assert pred[0, 2] == pred[1, 0] == pred[2, 0] == pred[2, 2] == 0
    assert ((d['alpha'] >= 0) & (d['alpha'] <= 1)).all()
    np.testing.assert_allclose(pred, (1-d['alpha'][:, None])*d['prior']+d['alpha'][:, None]*d['local'])


def test_abstain_and_fallback():
    m = NeighborhoodTrustTwin().fit([[1, 0, 0], [0, 1, 0]], [[1, 0, 0], [0, 1, 0]])
    with pytest.raises(ValueError, match='absent'):
        m.predict([[0, 0, 1]])
    with pytest.raises(ValueError, match='nonempty'):
        m.predict([[0, 0, 0]])
    pred, d = m.predict_with_details([[1, 1, 0]])
    np.testing.assert_allclose(pred, [[.5, .5, 0]])
    assert not d['fallback'][0]


def test_training_mismatch_and_leakage_support():
    with pytest.raises(ValueError, match='support'):
        NeighborhoodTrustTwin().fit([[1, 0]], [[0, 1]])
    with pytest.raises(ValueError, match='aligned'):
        NeighborhoodTrustTwin().fit([[1, 0]], [[1, 0], [1, 0]])
