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
