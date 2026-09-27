import json
from pathlib import Path


def test_gut_family_source_diagnostic_stays_unknown():
    d=json.loads(Path('results/gut_family_evidence.json').read_text())
    assert d['study']=='MGYS00005154'
    assert d['bioproject']=='PRJEB3079' and d['secondary_accession']=='ERP001500'
    assert d['declared_samples']==d['retrieved_samples']==529
    assert d['possible_participant_or_family_key_counts']=={}
    assert d['source_family_independence_status']=='unknown'
    assert len(d['sample_sources'])==3
    assert sum(p['items'] for p in d['sample_sources'])==529
    assert d['linked_publications'][0]['doi']=='10.1016/j.csbj.2021.07.009'
    assert all(len(p['sha256'])==64 for p in d['sample_sources'])
    assert 'sample' not in ' '.join(d['possible_participant_or_family_key_counts'])
