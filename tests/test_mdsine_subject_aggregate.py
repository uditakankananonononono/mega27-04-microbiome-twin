import json
from pathlib import Path
import subprocess
import sys


def test_subject_aggregate_matches_archived_pair_counts():
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/'scripts'))
    from mdsine_subject_aggregate import summarize
    for cohort, count in [('healthy',4),('uc',5)]:
        for alltp in (False,True):
            r=summarize(cohort,alltp)
            assert r['n_subjects']==count and len(r['source_sha256'])==64
            assert len(r['comparisons']['MDSINE2 (No Modules)']['per_subject'])==count
            assert all(x['taxon_pairs'] > 0 for x in r['comparisons']['MDSINE2 (No Modules)']['per_subject'])
