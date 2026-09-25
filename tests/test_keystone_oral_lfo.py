import json

def test_lfo_verdict():
    j=json.load(open('results/keystone_oral_lfo.json'))
    assert j['G1_pass']==(len(j['eligible_families'])>=3)
    assert j['LFO1_pass']==(j['G1_pass'] and all(r['coef_oral']>0 and r['p_oral']<0.05 for f in j['deleted'].values() for r in f.values()))
    assert set(j['deleted'])==set(j['eligible_families'])
