import json

def test_shap_attribution():
    j=json.load(open('results/keystone_shap.json'))
    assert j['G1_pass'] == (j['n_genera']>=180)
    assert j['SH1_pass'] == (j['G1_pass'] and j['ranked_features'][0]=='GAI')
    assert set(j['mean_abs'])=={'GAI','lra','log_ena'}

def test_symbolic_invariants():
    j=json.load(open('results/keystone_sympy.json'))
    assert j['SY1_pass']==j['G1_pass']==all(j[k]['tangent_zero'] and all(j[k]['boundary_zero']) for k in ('cnode','glv'))
