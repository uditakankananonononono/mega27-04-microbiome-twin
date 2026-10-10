import copy,json
import pytest
from microtwin.nested_perturbation_design import screen_nested_design,load_nested_design
from microtwin.cli import main


def fixture():
    rows=[]
    for e in ['e1','e2']:
        for batch in ['b1','b2','b3']:
            for c,token in [('control',None),('removal','A'),('removal','B')]:
                for w in ['w1','w2','w3']:
                    rows.append(dict(study='synthetic',experiment=e,biological_unit=batch+'-'+(token or 'full'),technical_unit=w,condition=c,control='full',batch=batch,medium='AF',time=4,removed_token=token,identity_verified=True))
    return dict(schema='microtwin.nested-perturbation.metadata.v1',expected_technical_units=3,minimum_biological_pairs=3,records=rows)

def reasons(d):return {r['reason'] for r in screen_nested_design(d)['unresolved_reasons']}

def test_valid_not_source_verified():
    r=screen_nested_design(fixture())
    assert r['status']=='METADATA_READY_FOR_MANUAL_DESIGN_REVIEW'
    assert r['technical_record_count']==54 and r['declared_biological_unit_count']==18
    assert r['complete_label_pair_count']==12
    assert not r['outcome_admitted'] and not r['biological_identity_source_verified']

def test_unverified_identity_and_incomplete_well():
    d=fixture();d['records'][0]['identity_verified']=False;d['records'].pop()
    assert {'BIOLOGICAL_IDENTITIES_UNVERIFIED','INCOMPLETE_TECHNICAL_REPLICATION','INSUFFICIENT_COMPLETE_BIOLOGICAL_PAIRS'}<=reasons(d)

def test_conflicting_treatment_and_duplicate_well():
    d=fixture();d['records'][3]['biological_unit']=d['records'][0]['biological_unit'];d['records'][3]['technical_unit']='w4'
    assert 'CONFLICTING_BIOLOGICAL_TREATMENT' in reasons(d)
    d=fixture();d['records'].append(copy.deepcopy(d['records'][0]))
    with pytest.raises(ValueError):screen_nested_design(d)

def test_unbalanced_and_no_controls():
    d=fixture();d['records']=[r for r in d['records'] if not (r['experiment']=='e2' and r['removed_token']=='B')]
    assert 'CONDITION_EXPERIMENT_IMBALANCE' in reasons(d)
    d['records']=[r for r in d['records'] if r['condition']!='control']
    assert {'UNMATCHED_OR_INCOMPLETE_CONTROL_PAIRS','NO_COMPLETE_LABEL_PAIRS'}<=reasons(d)

@pytest.mark.parametrize('field,value',[('literal','PRIVATE-RAW'),('condition','PRIVATE-RAW'),('identity_verified',1),('biological_unit',{}),('time',True),('removed_token',{})])
def test_bad_fields_non_echoing(field,value):
    d=fixture();d['records'][0][field]=value
    with pytest.raises(ValueError) as e:screen_nested_design(d)
    assert str(e.value)=='nested perturbation metadata rejected'

def test_loader_and_cli(tmp_path,capsys):
    p=tmp_path/'metadata.json';p.write_text(json.dumps(fixture()))
    assert main(['check-nested-perturbation-design',str(p)])==0
    p.write_text('{"private":"PRIVATE-RAW"}')
    assert main(['check-nested-perturbation-design',str(p)])==2
    assert 'PRIVATE-RAW' not in capsys.readouterr().err

def test_omm12_metadata_stays_blocked():
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    r=load_nested_design(root/'results/omm12_nested_design_metadata_20261010.json')
    assert r['status']=='BLOCKED'
    assert r['technical_record_count']==222
    assert 'BIOLOGICAL_IDENTITIES_UNVERIFIED' in {x['reason'] for x in r['unresolved_reasons']}
    assert not r['outcome_admitted']

def test_ambiguous_control_denies_pairing():
    d=fixture();extra=copy.deepcopy(d['records'][0]);extra['biological_unit']='second-control';extra['technical_unit']='other'
    d['records'].append(extra)
    assert 'AMBIGUOUS_CONTROL_MATCH' in reasons(d)

def test_mouse_style_same_identity_different_region_conflict():
    d=fixture();r=copy.deepcopy(d['records'][0]);r.update(medium='Ce',biological_unit='mouse2546')
    t=copy.deepcopy(r);t.update(medium='F',condition='removal',removed_token='KB1')
    d['records']=[r,t]
    assert 'CONFLICTING_BIOLOGICAL_TREATMENT' in reasons(d)
