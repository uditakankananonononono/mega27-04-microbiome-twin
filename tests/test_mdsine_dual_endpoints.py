from pathlib import Path
import json
import sys


def test_dual_endpoint_reproduces_archived_conditional_metric():
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/'scripts'))
    from mdsine_dual_endpoints import run
    for cohort,n in [('healthy',4),('uc',5)]:
        result=run(cohort)
        stored=json.loads((root/f'results/mdsine_dual_{cohort}.json').read_text())
        assert result==stored
        assert result['mouse_count']==n
        for method in result['methods'].values():
            assert method['n_timepoints']==sum(method[k] for k in ['tp','tn','fp','fn'])
            assert method['pair_count']>=n
