import pandas as pd
import pytest
from microtwin.transfer_coverage import vocabulary_coverage


def test_retained_count_mass_not_just_name_overlap():
    t=pd.DataFrame({'s1':[9,1],'s2':[1,9]},index=['shared','unseen'])
    r=vocabulary_coverage(['shared','train_only'],t)
    assert r['shared_genera']==1 and r['median_test_mass_covered']==pytest.approx(.5)
    assert r['minimum_test_mass_covered']==pytest.approx(.1)


def test_no_outcome_from_zero_mass():
    with pytest.raises(ValueError,match='zero-mass'):
        vocabulary_coverage(['x'],pd.DataFrame({'s':[0]},index=['x']))
