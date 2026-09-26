from pathlib import Path
import sys


def test_oral_pilot_person_sensitivity_units_and_reproducibility():
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/'scripts'))
    from oral_pilot_person_sensitivity import summarize
    a=summarize()
    assert a==summarize()
    assert a['test_people']==58
    assert a['bootstrap_unit']=='person'
    assert set(a['comparisons'])=={'cnode','glv','graphtwin','transformer'}
    for r in a['comparisons'].values():
        assert r['people_model_better']+r['people_prior_better']+r['people_tied']==58
