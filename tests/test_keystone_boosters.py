import json

def test_booster_verdicts():
    for kind in ('lightgbm','catboost'):
        j=json.load(open(f'results/keystone_{kind}.json'))
        assert j['G1_pass']==(j['n_genera']>=180)
        assert j['B1_pass']==(j['G1_pass'] and j['r2_full_mean']>0 and j['delta_mean']>0 and j['n_positive']>=15)
        assert 0<=j['n_positive']<=20
