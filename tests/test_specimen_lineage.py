import copy,json
from pathlib import Path
import pytest
from microtwin.specimen_lineage import screen_lineage,load_lineage
from microtwin.cli import main

def fixture():
    rows=[dict(source='synthetic',subject='person1',specimen='specimen1',collection='day1',material='stool',modality=m,aliquot_group='split1',technical='t1',condition='full',lineage_verified=True) for m in ['qPCR','SCFA']]
    return dict(schema='microtwin.specimen-lineage.metadata.v1',records=rows,minimum_paired_specimens=1)

def reasons(d):return {r['reason'] for r in screen_lineage(d)['unresolved_reasons']}

def test_submitted_pair_never_certifies_physical():
    r=screen_lineage(fixture());assert r['status']=='METADATA_READY_FOR_MANUAL_LINEAGE_REVIEW'
    assert r['submitted_verified_specimen_pairs']==1 and not r['physical_aliquot_source_verified']
    assert 'person1' not in str(r) and not r['outcome_admitted']

def test_same_person_different_specimens_not_pair():
    d=fixture();d['records'][1]['specimen']='different'
    r=screen_lineage(d);assert r['shared_subject_labels']==1 and r['submitted_verified_specimen_pairs']==0

@pytest.mark.parametrize('field,value',[('collection','day2'),('material','blood'),('condition','dropout'),('subject','other')])
def test_same_specimen_conflicting_provenance(field,value):
    d=fixture();d['records'][1][field]=value
    assert 'SPECIMEN_PROVENANCE_CONFLICT' in reasons(d)

def test_aliquot_mismatch_unknown_and_repeats():
    d=fixture();d['records'][1]['aliquot_group']='different'
    assert 'ALIQUOT_LINEAGE_CONFLICT' in reasons(d)
    d=fixture();r=copy.deepcopy(d['records'][0]);r['technical']='t2';d['records'].append(r)
    out=screen_lineage(d);assert out['submitted_verified_specimen_pairs']==1 and out['technical_repeat_rows_not_additional_specimens']==1
    d['records'].append(copy.deepcopy(r))
    with pytest.raises(ValueError):screen_lineage(d)

@pytest.mark.parametrize('field,value',[('raw_value','PRIVATE-RAW'),('modality','unknown'),('lineage_verified',1),('subject',{}),('specimen',[]),('aliquot_group',None)])
def test_reject_raw_unknown_without_echo(field,value):
    d=fixture();d['records'][0][field]=value
    with pytest.raises(ValueError) as e:screen_lineage(d)
    assert str(e.value)=='specimen lineage metadata rejected'

def test_omm12_unknown_specimen_stays_blocked():
    root=Path(__file__).resolve().parents[1]
    r=load_lineage(root/'results/omm12_specimen_lineage_metadata_20261010.json')
    assert r['status']=='BLOCKED' and r['shared_subject_labels']==30
    assert r['metadata_rows']==60 and r['submitted_verified_specimen_pairs']==0
    assert r['cross_modality_specimen_label_candidates']==0

def test_cli_no_echo(tmp_path,capsys):
    p=tmp_path/'metadata.json';p.write_text(json.dumps(fixture()))
    assert main(['check-specimen-lineage',str(p)])==0
    p.write_text('{"private":"PRIVATE-RAW"}')
    assert main(['check-specimen-lineage',str(p)])==2
    out=capsys.readouterr();assert 'PRIVATE-RAW' not in out.out+out.err

def test_ambiguous_specimen_candidates_block():
    d=fixture();r=copy.deepcopy(d['records'][0]);r.update(specimen='second',technical='t2');d['records'].append(r)
    assert 'AMBIGUOUS_SPECIMEN_JOIN' in reasons(d)
