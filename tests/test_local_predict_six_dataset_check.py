import json
from pathlib import Path
import sys

import numpy as np
from microtwin.data import load
from microtwin.models import PresenceMean


def test_crossvalidation_result_matches_archived_baseline():
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/'scripts'))
    from local_predict_six_dataset_check import score_dataset
    result=score_dataset('Human_Oral')
    archived=json.loads(next((root/'results').glob('bench_Human_Oral_presence_mean_cnode_glv_graphtwin_k*.json')).read_text())
    assert result['samples_after_assemblage_dedup']==len(archived['errors']['presence_mean'])
    assert result['median_bray_curtis']==np.median(archived['errors']['presence_mean'])
    z,p=load('Human_Oral')
    baseline=PresenceMean().fit(z[:-1],p[:-1]).predict(z[-1:])
    expected=z[-1:] * (p[:-1].mean(0)+1e-9)
    expected/=expected.sum(1,keepdims=True)
    np.testing.assert_allclose(baseline,expected)
