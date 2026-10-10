"""Create synthetic metadata fixtures only, no source or outcome access.

python -m microtwin.admission_demo NEW_DIRECTORY
"""
import json
from pathlib import Path
from .admission_boundary import STATUS,check_boundary
from .admission_evidence_bundle import FILES


def create_demo(path):
    p=Path(path)
    if p.exists():raise ValueError('synthetic fixture directory must be new')
    p.mkdir(parents=True)
    taxa=['KB1','YL2','KB18','YL27','YL31','YL32','YL44','YL45','I46','I48','I49','YL58']
    keys=[f'{condition}_E{e}_{medium}_W{w}' for condition in ['OMM12']+['OMM11-'+t for t in taxa] for e in range(1,4) for medium in ['AF','APF'] for w in range(1,4)][:222]
    manifest=[{'sample_key':k,'addresses':[f'{c}{r}' for c in 'BCDEFGHIJKLM']} for r,k in enumerate(keys,2)]
    d=dict(STATUS,source_sha256='0'*64,parent_decision_at='2026-01-01T00:00:00+00:00',selected_rows=222,allowed_cells=2664,manifest=manifest,representation_counts={'AMBIGUOUS_ZERO':2664,'NUMERIC_REPRESENTATION_VALID':0},issues=[])
    # Deliberately synthetic statuses, NOT an authenticated grant/source result.
    report=check_boundary(d)
    for role,title in [('proposal','# OMM12 outcome-admission proposal v1,'),('closeout','# OMM12 documentary closeout,')]:
        (p/FILES[role]).write_text(title+' SYNTHETIC TEST ONLY\n\nNo real approval, source, rights or outcomes. This is a metadata schema exercise.\n')
    for role,obj in [('certificate',d),('boundary_check',report)]:
        (p/FILES[role]).write_text(json.dumps(obj,indent=2)+'\n')
    return {'status':'synthetic_metadata_fixtures_created','real_source_or_approval':False}

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('directory');a=ap.parse_args()
    print(json.dumps(create_demo(a.directory)))
