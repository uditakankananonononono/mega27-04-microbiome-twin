import numpy as np
import pytest
from microtwin.ambiguity_certificate import certify_three_species_removal


@pytest.mark.parametrize('interval,expected', [((-.4,.4),True),((.1,.4),False),((-.4,-.1),False),((0,.4),False),((0,0),False)])
def test_frozen_panel(interval,expected):
    d=certify_three_species_removal(*interval)
    assert (d['status']=='opposite_sign_witness') is expected
    if expected:
        assert len(d['witnesses'])==2
        assert d['witnesses'][0]['target_change']>0>d['witnesses'][1]['target_change']
        for w in d['witnesses']:
            a=np.array(w['interaction_matrix']);r=np.array(w['intrinsic_rates'])
            x=np.array(w['observed_equilibrium']);post=np.array(w['post_removal_equilibrium'])
            np.testing.assert_allclose(x*(r+a@x),0,atol=1e-12)
            np.testing.assert_allclose(post[:2]*(r[:2]+a[:2,:2]@post[:2]),0,atol=1e-12)
            assert np.linalg.eigvals(np.diag(x)@a).real.max()<0
            assert np.linalg.eigvals(np.diag(post[:2])@a[:2,:2]).real.max()<0


@pytest.mark.parametrize('interval',[(-1,.4),(-.1,.9),(.4,-.4),(float('nan'),.2),(True,.3)])
def test_invalid_bounds_fail_closed(interval):
    with pytest.raises(ValueError,match='interval'):
        certify_three_species_removal(*interval)
