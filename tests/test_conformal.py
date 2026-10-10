import numpy as np
import pytest

from microtwin.conformal import bray_radius


def test_split_conformal_rank_and_vacuous_small_sample():
    assert bray_radius([.3, .1, .4, .2], .2)['radius'] == .4
    assert bray_radius([.3, .1, .4, .2], .1)['radius'] == 1.
    assert bray_radius([.3, .1, .4, .2], .1)['vacuous'] is True


@pytest.mark.parametrize('scores', [[-1], [1.1], [np.nan], [], [[.2]]])
def test_reject_invalid_calibration(scores):
    with pytest.raises(ValueError):
        bray_radius(scores)


def test_internal_split_accounting_and_hashes():
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
    from internal_conformal_check import evaluate
    row = evaluate('Drosophila_Gut')
    assert row['train'] + row['calibration'] + row['test'] == 24
    assert row['calibration'] == 4 and row['vacuous'] is True
    assert row['covered_test'] == row['test']
    assert len(row['source_sha256']) == 64


@pytest.mark.parametrize('alpha', [float('nan'), float('inf'), True, '0.1', 0, 1])
def test_invalid_alpha_fails_with_validation_error(alpha):
    with pytest.raises(ValueError, match='alpha'):
        bray_radius([.2, .3], alpha)


def test_metric_maximum_caps_accepted_roundoff():
    result=bray_radius([1+5e-11],.5)
    assert result['radius']==1.0 and result['vacuous'] is False
    with pytest.raises(ValueError,match='within'):
        bray_radius([1+2e-10],.5)


@pytest.mark.parametrize('scores', [['PRIVATE_VALUE'], [10**1000], object()])
def test_conversion_failure_fixed_private_safe_error(scores):
    with pytest.raises(ValueError) as error:
        bray_radius(scores)
    assert str(error.value)=='finite numeric calibration errors required'
