import importlib.util
from pathlib import Path
import numpy as np


def test_interval_constant_and_translation():
    spec=importlib.util.spec_from_file_location('precision',Path('scripts/hierarchical_precision.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    assert np.allclose(m.interval_mean(np.ones(4)*3,np.random.default_rng(7)),[3,3])
    a=m.interval_mean([1,2,3,4],np.random.default_rng(7))
    b=m.interval_mean([6,7,8,9],np.random.default_rng(7))
    assert np.allclose(b-a,5)


def test_frozen_result_grid():
    import json,itertools
    r=json.loads(Path('results/hierarchical_precision_20261007.json').read_text())
    actual={(x['subjects'],x['repeats'],x['rho'],x['true_gap']) for x in r['cells']}
    assert actual==set(itertools.product([4,5,10,20],[1,10,25],[0.,.5,.9],[0.,.25]))
    assert r['cell_count']==72 and r['panels']==7200 and r['intervals']==14400
    assert r['useful_win'] is False
    for x in r['cells']:
        for k in ['naive','cluster']:
            v=x[k];p=v['coverage']
            assert 0<=p<=1 and 0<=v['positive_exclusion_rate']<=1 and v['mean_width']>=0
            assert np.isclose(v['coverage_mc_se'],np.sqrt(p*(1-p)/100))
