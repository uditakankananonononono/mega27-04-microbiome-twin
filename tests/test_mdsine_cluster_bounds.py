import sys
from pathlib import Path
import pytest


def test_exact_mouse_level_bounds_are_not_taxon_resampling():
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/'scripts'))
    from mdsine_cluster_bounds import mouse_cluster_bounds
    h=mouse_cluster_bounds('healthy','detected')
    u=mouse_cluster_bounds('uc','all')
    assert h['mouse_count']==4 and h['bootstrap_resamples_enumerated']==4**4
    assert u['mouse_count']==5 and u['bootstrap_resamples_enumerated']==5**5
    assert h['cluster_bootstrap95'][0]<0<h['cluster_bootstrap95'][1]
    assert u['cluster_bootstrap95'][1]<0
    with pytest.raises(ValueError):mouse_cluster_bounds('other','all')
