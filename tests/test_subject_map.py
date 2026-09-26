import pytest
from microtwin.subject_map import oral_subject_map


def _r(sid,name,desc):return {'id':sid,'attributes':{'sample-name':name,'sample-desc':desc}}


def test_paired_sites_share_person():
    out=oral_subject_map([_r('S1','PK501D','Paper point sample from diseased area of diseased individual'),
                         _r('S2','PK501H','Paper point sample of healthy area of diseased individual')])
    assert out['samples']==2 and out['subjects']==1
    assert out['mapping']['S1']['subject']==out['mapping']['S2']['subject']=='PK501'


def test_unsupported_description_fails_closed():
    with pytest.raises(ValueError):oral_subject_map([_r('S1','PK501D','unknown')])
