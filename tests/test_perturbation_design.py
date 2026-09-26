import pytest
from microtwin.perturbation_design import screen_paired_design


def rows():
    out=[]
    for arm in ('intervention','control'):
        for i in range(2):
            for t in (-2,3):
                out.append({'study':'trial','phase':'p1','subject':f'{arm}-{i}',
                            'sample':f'{arm}-{i}-{t}','arm':arm,'time':t})
    return out


def test_two_arms_are_paired_but_no_effect_claim():
    x=screen_paired_design(rows(),baseline_end=-1,followup_start=2)
    assert x['eligible_phases_on_design_only']==1
    assert x['phases'][0]['paired_intervention_subjects']==2
    assert x['status']=='design_screen_only_no_outcomes'


def test_one_arm_or_unpaired_phase_is_not_eligible():
    x=screen_paired_design([r for r in rows() if not (r['arm']=='control' and r['time']==3)],
                            baseline_end=-1,followup_start=2)
    assert x['eligible_phases_on_design_only']==0 and x['phases'][0]['unpaired_subjects']==2


def test_label_leakage_and_duplicate_are_rejected():
    bad=rows();bad.append(dict(bad[0]))
    with pytest.raises(ValueError,match='duplicate sample'):screen_paired_design(bad)
    bad=rows();bad[-1]['arm']='intervention'
    with pytest.raises(ValueError,match='switches'):screen_paired_design(bad)
    bad=rows();bad[-1]['study']='other'
    with pytest.raises(ValueError,match='multiple studies'):screen_paired_design(bad)
    bad=rows();bad[0]['phase']=''
    with pytest.raises(ValueError,match='labels'):screen_paired_design(bad)
