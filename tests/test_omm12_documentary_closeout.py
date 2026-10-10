import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def data():
    return json.loads((ROOT/'results/omm12_documentary_closeout_20261010.json').read_text())

def test_closeout_has_no_admission():
    d=data()
    assert d['outcome_access'] is False
    assert d['status']=='DOCUMENTARY_CLOSEOUT_NOT_ADMITTED'
    assert d['lane_next_step']=='PAUSE_FOR_OUTCOME_ADMISSION_PROPOSAL_REVIEW'
    assert len(d['unresolved_register'])==10
    assert all(x['status']=='UNRESOLVED' for x in d['unresolved_register'])

def test_candidate_identity_not_applied():
    d={x['strain_token']:x for x in data()['identity_crosswalk']}
    assert len(d)==12
    assert d['YL44']['DSM_2022']=='DSM26127'
    assert d['YL44']['DSM_2023']=='DSM26109'
    assert d['YL44']['status']=='CANDIDATE_CORRECTION_NOT_APPLIED'
    assert d['YL45']['DSM_2022']=='DSM26109'

def test_mouse_conflict_retained_not_corrected():
    d=data()
    assert len(d['mouse_sample_metadata'])==179
    rows=[x for x in d['mouse_sample_metadata'] if x['mouse_id']=='2546']
    assert {(x['region'],x['condition']) for x in rows}=={('Ce','OMM12'),('F','OMM-KB1'),('Il','OMM-KB1'),('Je','OMM-KB1')}
    assert len(d['control_pairs_syntax_only'])==207
    assert all(x['status']=='SYNTAX_MATCH_ONLY' for x in d['control_pairs_syntax_only'])
