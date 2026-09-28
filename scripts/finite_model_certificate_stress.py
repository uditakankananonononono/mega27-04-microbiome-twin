"""Locked constructed 40-pair panel and invalid-input checks."""
import json
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from microtwin.finite_model_certificate import certify_finite_candidates


def model(c,a01,a10):
    a=np.diag([-1.,-1.,-1.]);a[0,1]=a01;a[1,0]=a10;a[0,2]=c
    r=-a@np.ones(3)
    return {'A':a.tolist(),'r':r.tolist()}


def run():
    rng=np.random.default_rng(20260928);panel=[]
    for i in range(40):
        a01,a10=rng.uniform(-.15,.15,size=2)
        if i<20:c1,c2=rng.uniform(-.7,-.2),rng.uniform(.2,.7);expected=True
        else:c1,c2=rng.uniform(.2,.7,size=2);expected=False
        panel.append((expected,[model(c1,a01,a10),model(c2,a01,a10)]))
    order=rng.permutation(40)
    rows=[]
    strict_detected=0;strict_abstained=0
    for i in order:
        expected,c=panel[int(i)];d=certify_finite_candidates(c,[1,1,1])
        strict=certify_finite_candidates(c,[1,1,1],require_global_reachability=True)
        assert strict['valid_count']==2 and strict['rejected_count']==0
        strict_detected+=int(expected and strict['status']=='opposite_sign_witness')
        strict_abstained+=int(not expected and strict['status']!='opposite_sign_witness')
        for w in strict['witnesses']:
            a=np.asarray(w['interaction_matrix'])
            assert np.linalg.eigvalsh((a[:2,:2]+a[:2,:2].T)/2).max()<-1e-7
        rows.append({'case_index':int(i),'constructed_opposition':expected,'witness':d['status']=='opposite_sign_witness',
                     'valid_count':d['valid_count'],'rejected_count':d['rejected_count'],
                     'target_changes':[float(-m['A'][0][2]/(1-m['A'][0][1]*m['A'][1][0])) for m in c]})
        # Signs and residuals must be independently recomputed from submitted witness, not returned metadata.
        for w in d['witnesses']:
            a=np.array(w['interaction_matrix']);r=np.array(w['intrinsic_rates']);x=np.ones(3)
            post=np.linalg.solve(a[:2,:2],-r[:2]);delta=float(post[0]-1)
            assert abs(delta-w['target_change'])<1e-10
            assert np.max(abs(x*(r+a@x)))<1e-10
            assert np.max(abs(post*(r[:2]+a[:2,:2]@post)))<1e-10
            assert np.linalg.eigvals(np.diag(x)@a).real.max()<-1e-7
            assert np.linalg.eigvals(np.diag(post)@a[:2,:2]).real.max()<-1e-7
    invalid=[{'A':model(.3,0,0)['A'],'r':[float('nan'),1,1]},
             {'A':model(.3,0,0)['A'],'r':[0,0,0]},
             {'A':np.diag([1.,-1.,-1.]).tolist(),'r':[-1.,1.,1.]}]
    rejected=certify_finite_candidates([model(-.3,0,0),*invalid,model(.3,0,0)],[1,1,1])
    assert rejected['rejected_count']==3 and rejected['status']=='opposite_sign_witness'
    return {'protocol':'results/PREREG_20260928_finite_model_ambiguity.md',
            'scope':'constructed synthetic paired models only, no real-source results',
            'opposing_pairs':20,'one_sided_pairs':20,
            'opposing_detected':sum(r['witness'] for r in rows if r['constructed_opposition']),
            'one_sided_abstained':sum(not r['witness'] for r in rows if not r['constructed_opposition']),
            'weak_any_distinct_A_flagged':40,'invalid_injected_rejected':rejected['rejected_count'],
            'lyapunov_opposing_detected':strict_detected,'lyapunov_one_sided_abstained':strict_abstained,
            'cases':rows}

if __name__=='__main__':
    d=run();out=ROOT/'results/finite_model_certificate_stress.json';out.write_text(json.dumps(d,indent=2)+'\n')
    print(out,d['opposing_detected'],d['one_sided_abstained'],d['invalid_injected_rejected'])
