import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def dictionary():
    return json.loads((ROOT/'results/omm12_structural_dictionary_20261010.json').read_text())

def test_structural_only_not_admitted():
    d = dictionary()
    assert d['status'] == 'STRUCTURALLY_REVIEWED_NOT_ADMITTED'
    assert d['numeric_outcomes_extracted'] is False
    assert len(d['admission_blockers']) == 9
    assert len(d['sheets']) == 22
    assert all(set(h) == {'cell', 'text'} for s in d['sheets'] for h in s['header_labels'])

def test_nonuniform_replication_preserved():
    c = {(x['condition'],x['medium']):x for x in dictionary()['main_screen_label_counts']}
    assert sum(x['row_labels'] for x in c.values()) == 228
    assert c['OMM12','APF']['row_labels'] == 12
    assert c['OMM11-YL44','APF']['batch_labels'] == ['E2','E3']
    assert c['OMM11-I48','APF']['batch_labels'] == ['E2','E3','S1new']

def test_repeated_and_distinct_populations_retained():
    d=dictionary()
    assert d['within_workbook_identifier_overlaps']['Tab13_Tab14']==179
    assert d['mouse_id_overlap']['SCFA_bile_acid']==20
    assert d['mouse_id_overlap']['LCN2_histology']==10
    assert d['mouse_id_overlap']['LCN2_weight']==0
    assert d['mouse_metadata_row_counts']['Tab16']==37
