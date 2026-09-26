import sys
from pathlib import Path

import numpy as np


def test_paired_site_units_and_reproducibility():
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / 'scripts'))
    from oral_paired_site_diagnostic import summarize
    a, b = summarize(), summarize()
    assert a == b
    assert (a['paired_people'], a['total_people']) == (29, 58)
    assert set(a['models']) == {'presence_mean', 'cnode', 'glv', 'graphtwin', 'transformer'}
    assert np.isclose(a['models']['presence_mean']['mean_D_minus_H_error'], -0.004727678535644978)
