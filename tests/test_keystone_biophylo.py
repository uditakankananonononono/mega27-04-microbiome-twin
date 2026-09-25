import json

def test_topology_verdict():
    j=json.load(open('results/keystone_biophylo.json'))
    assert j['G1_pass']==(j['n_tips']>=100 and j['n_oral']>=20)
    assert j['BP1_pass']==(j['G1_pass'] and j['p_one_sided']<0.05)
    assert 0<j['p_one_sided']<=1
