from pathlib import Path
import sys


def test_oral_predictive_gain_uses_one_study_not_58_independent_studies():
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/'scripts'))
    from oral_pilot_dependence import summarize
    r=summarize('graphtwin')
    assert r['people']==58 and r['people_scored']==58
    assert r['independent_studies']==1
    assert r['study_level_interval'] is None
    assert r['interval_status']=='insufficient_independent_groups'
