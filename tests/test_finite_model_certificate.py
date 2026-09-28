import numpy as np
import pytest
from microtwin.finite_model_certificate import certify_finite_candidates


def model(c):
    a=np.diag([-1.,-1.,-1.]);a[0,2]=c
    return {'A':a.tolist(),'r':(-a@np.ones(3)).tolist()}


def test_witness_and_abstention():
    d=certify_finite_candidates([model(-.3),model(.3)],[1,1,1])
    assert d['valid_count']==2 and d['positive_count']==d['negative_count']==1
    assert d['witnesses'][0]['target_change']>0>d['witnesses'][1]['target_change']
    assert certify_finite_candidates([model(.2),model(.4)],[1,1,1])['status'].startswith('abstain')


def test_rejections_do_not_create_evidence():
    bad=model(.3);bad['r'][0]=0
    d=certify_finite_candidates([bad,model(.2)],[1,1,1])
    assert d['rejected_count']==1 and d['status'].startswith('abstain')
    with pytest.raises(ValueError,match='baseline'):
        certify_finite_candidates([model(.2)],[1,0,1])
