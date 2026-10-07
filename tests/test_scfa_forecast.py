from datetime import datetime, timedelta
import numpy as np
import pytest
from microtwin.scfa_forecast import ANALYTES, prepare, folds, forecast_fold, evaluate


def fixture(n=50):
    metadata=[];assay=[]
    for i in range(n):
        for t in ('T1','T2','T3','T4'):
            name=f's{i}-{t}'
            metadata.append({'sample_name':name,'Participant_ID':f'p{i:03d}', 'Timepoint':t,
                'Iteration':'1','Group':'A' if i<n//2 else 'B',
                'collection_date':datetime(2026,1,1)+timedelta(days=28*(int(t[1])-1))})
            for a in ANALYTES:
                assay.append({'Client Sample ID':name,'Analyte':a,'Unit':'µg/g','Client Matrix':'Feces',
                    'Results':10+i,'LLOQ':1.,'ULOQ':1000.,'Analysis Comments':None})
    return metadata,assay


def test_prepare_counts_and_future_values_invariance():
    m,a=fixture();ids,g,x,y,r=prepare(m,a)
    assert r['evaluable'] and r['eligible_subjects']==50
    for row in a:
        if row['Client Sample ID'].endswith(('T3','T4')):row['Results']='FUTURE-UNAVAILABLE'
    ids2,g2,x2,y2,r2=prepare(m,a)
    assert ids==ids2 and r==r2 and np.array_equal(x,x2) and np.array_equal(y,y2)


def test_duplicate_qc_values_cannot_enter_first_period():
    m,a=fixture();base=prepare(m,a)
    m.append({**m[0],'sample_name':'qc','Iteration':'2'})
    for row in a[:8]:a.append({**row,'Client Sample ID':'qc','Results':'QC-UNAVAILABLE'})
    later=prepare(m,a)
    assert base[0]==later[0] and np.array_equal(base[2],later[2]) and base[4]==later[4]


@pytest.mark.parametrize('field,value',[('Unit','mg/g'),('Results',float('nan')),('Results',-1),
    ('Analysis Comments','BLOQ'),('LLOQ',None),('ULOQ',1)])
def test_assay_invalidity_rejected_or_excluded(field,value):
    m,a=fixture();a[0][field]=value
    if field=='Unit':
        with pytest.raises(ValueError):prepare(m,a)
    else:
        r=prepare(m,a)[4]
        assert r['eligible_subjects']==49 and r['exclusions']['assay_complete_case_failure']==1


def test_dates_filter_before_fit_and_sample_size_stop():
    m,a=fixture(40);m[1]['collection_date']=datetime(2027,1,1)
    r=prepare(m,a)[4]
    assert r['exclusions']['outside_21_35_day_window']==1 and not r['evaluable']


def test_duplicate_record_and_conflicting_group_rejected():
    m,a=fixture()
    with pytest.raises(ValueError,match='duplicate'):prepare(m,a+[a[0]])
    m[1]['Group']='B'
    with pytest.raises(ValueError,match='conflicting'):prepare(m,a)


def arrays():
    rng=np.random.default_rng(6);x=rng.uniform(1,100,(50,8));y=x+rng.uniform(0,5,(50,8))
    return [f'p{i:03d}' for i in range(50)], np.array(['A']*25+['B']*25),x,y


def test_outer_predictions_target_replacement_and_overlap_guard():
    ids,g,b,t=arrays();x,y=np.log1p(b),np.log1p(t);f=folds(ids,g)
    train,test=np.flatnonzero(f!=0),np.flatnonzero(f==0)
    p,sd=forecast_fold(x,y,g,ids,train,test);y[test]=999
    q,_=forecast_fold(x,y,g,ids,train,test)
    assert all(np.array_equal(p[k],q[k]) for k in p)
    with pytest.raises(ValueError,match='overlap'):forecast_fold(x,y,g,ids,train,train[:1])


def test_evaluation_reproducible_complete_and_scope_limited():
    args=arrays();r=evaluate(*args);assert r==evaluate(*args)
    assert sum(r['fold_sizes'].values())==r['subjects_scored']==50
    assert r['all_predictions_finite'] and r['target_replacement_invariance']
    assert set(r['comparisons'])=={'persistence','arm_mean','nearest_three'}
    assert 'same-study' in r['scope']

def test_frozen_useful_threshold_not_weakened_by_observed_result():
    import json
    from pathlib import Path
    r=json.loads(Path('results/scfa_first_period_forecast_20261007.json').read_text())
    e=r['evaluation']
    assert e['subjects_scored']==84 and not e['useful_win']
    assert e['comparisons']['nearest_three']['relative_error_reduction'] < .1
    assert all(v['bootstrap_95_percent_interval'][1]<0 for v in e['comparisons'].values())
