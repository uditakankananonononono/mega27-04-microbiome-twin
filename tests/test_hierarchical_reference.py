import importlib.util,sys
from pathlib import Path
import numpy as np


def load():
    sys.path.insert(0,'scripts')
    spec=importlib.util.spec_from_file_location('reference',Path('scripts/hierarchical_reference.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def test_reference_interval_formula():
    m=load();a=m.reference_intervals([1,2,3,4],1)
    assert np.allclose(a['known_variance_oracle'],[2.5-.97998199227,2.5+.97998199227])
    assert np.allclose(a['student_t'],[.44573974324,4.55426025676])
    b=m.reference_intervals([6,7,8,9],1)
    assert all(np.allclose(b[k]-a[k],5) for k in a)


def test_result_grid_and_scope():
    import json,itertools
    r=json.loads(Path('results/hierarchical_reference_20261007.json').read_text())
    assert {(x['subjects'],x['repeats'],x['rho']) for x in r['cells']}==set(itertools.product([4,5,10,20],[1,25],[0.,.5,.9]))
    assert r['panels']==12000 and r['intervals']==36000 and r['useful_win'] is False
    for x in r['cells']:
        for k in ['cluster','student_t','known_variance_oracle']:
            p=x[k]['coverage']
            assert 0<=p<=1 and x[k]['mean_width']>=0
            assert np.isclose(x[k]['coverage_mc_se'],np.sqrt(p*(1-p)/500))
