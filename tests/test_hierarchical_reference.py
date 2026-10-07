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
