import numpy as np
from microtwin.finite_model_certificate import certify_finite_candidates


def model(a,c):
    a=np.array(a,dtype=float);a[0,2]=c
    return {'A':a.tolist(),'r':(-a@np.ones(3)).tolist()}


def test_global_certificate_retains_good_pair():
    a=np.diag([-1.,-1.,-1.]);a[0,1]=.1;a[1,0]=-.1
    d=certify_finite_candidates([model(a,-.4),model(a,.4)],[1,1,1],require_global_reachability=True)
    assert d['status']=='opposite_sign_witness'
    assert all(w['survivor_symmetric_part_max_eigenvalue']<0 for w in d['witnesses'])
    assert d['global_reachability_sufficient_condition_required']


def test_local_stability_is_not_sufficient_condition():
    a=np.diag([-1.,-1.,-1.]);a[0,1]=4
    candidate=model(a,.2)
    loose=certify_finite_candidates([candidate],[1,1,1])
    strict=certify_finite_candidates([candidate],[1,1,1],require_global_reachability=True)
    assert loose['valid_count']==1 and loose['status'].startswith('abstain')
    assert strict['valid_count']==0 and strict['rejected_count']==1
    # Rejection is a failure to certify, not a claim that this trajectory diverges.
