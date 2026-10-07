import json
import pytest
from microtwin.chemical_panel_admission import screen_chemical_panel


def rows(source='S'):
    return [dict(sample=f'x{i}',source_family=source,subject='PRIVATE-ID',arm='potato',phase='before' if i<3 else 'during',time=i,observed={'a':True,'b':True}) for i in range(6)]


def screen(r,**kw):
    return screen_chemical_panel(r,analytes=['a','b'],units_verified=kw.pop('units_verified',True),**kw)


def test_complete_and_privacy():
    result=screen(rows())
    assert result['joint_analyte_eligible_subjects']==result['complete_specimen_panel_eligible_subjects']==1
    assert result['status']=='metadata_eligible'
    assert 'PRIVATE-ID' not in json.dumps(result)
    assert not result['forecast_authorized'] and not result['independent_validation']


def test_presence_is_analyte_specific():
    r=rows();r[0]['observed']['b']=False
    result=screen(r)
    assert result['per_analyte_paired_eligible_subjects']=={'a':1,'b':0}
    assert result['joint_analyte_eligible_subjects']==0
    assert result['status']=='abstain'


def test_joint_not_same_specimen():
    r=rows();r[0]['observed']['a']=False;r[1]['observed']['b']=False
    result=screen(r,min_per_phase=2)
    assert result['joint_analyte_eligible_subjects']==1
    assert result['complete_specimen_panel_eligible_subjects']==0


def test_source_scoped_keys():
    result=screen(rows('S')+rows('T'))
    assert result['source_subject_keys']==2 and result['joint_analyte_eligible_subjects']==2


def test_temporal_leakage_abstains():
    r=rows();r[2]['time']=10
    result=screen(r)
    assert result['subjects_with_temporal_block']==1 and result['status']=='abstain'


def test_arm_conflict_abstains():
    r=rows();r[-1]['arm']='inulin'
    assert screen(r)['subjects_with_arm_conflict']==1


@pytest.mark.parametrize('change',[lambda r:r.append(r[0].copy()),lambda r:r[1].update(time=0),lambda r:r[0].update(phase='unknown'),lambda r:r[0]['observed'].update(a=1),lambda r:r[0].update(acetate=5.0),lambda r:r[0].update(time=True)])
def test_malformed_or_raw_values_rejected(change):
    r=rows();change(r)
    with pytest.raises(ValueError):screen(r)


def test_units_unverified_abstains():
    result=screen(rows(),units_verified=False)
    assert result['joint_analyte_eligible_subjects']==1 and result['status']=='abstain'


@pytest.mark.parametrize('kwargs',[{'min_per_phase':0},{'min_per_phase':True},{'units_verified':1}])
def test_settings_strict(kwargs):
    with pytest.raises(ValueError):screen(rows(),**kwargs)
