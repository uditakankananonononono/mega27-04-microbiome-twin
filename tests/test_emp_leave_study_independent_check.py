import sys
from pathlib import Path


def test_independent_formula_reconstructs_viewed_result():
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/'scripts'))
    from emp_leave_study_independent_check import check
    out=check()
    assert out['checked_studies']==16
    assert out['max_absolute_difference']<1e-10
    assert {r['study_id'] for r in out['rows']}=={662,722,804,807,910,925,933,940,1039,1453,1580,1642,1747,1774,2192,2229}
