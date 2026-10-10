import json
from pathlib import Path
import pytest
from microtwin.censor_contract import assess_censor_contract,load_censor_contract,VOCAB
from microtwin.cli import main

def fixture():return dict(schema='microtwin.censor-semantics.metadata.v1',unit='normalized_16S_copies_per_ml',normalization='verified_applied',zero_interpretation='true_zero',missing_convention='explicit_separate_flags',DTL_policy='censored_flagged',provenance_status='evidence_reviewed')

def test_ready_is_not_admitted():
    r=assess_censor_contract(fixture());assert r['status']=='SEMANTIC_DECLARATIONS_READY_FOR_MANUAL_REVIEW'
    assert not any(r[k] for k in ['quantitative_summary_eligible','effect_eligible','C1_admitted','values_consumed','conversion_or_imputation_performed'])

@pytest.mark.parametrize('field',list(VOCAB))
def test_unknown_never_defaults_ready(field):
    d=fixture();d[field]='unknown';assert assess_censor_contract(d)['status']=='ABSTAIN'

@pytest.mark.parametrize('zero',['below_DTL','excluded','missing'])
def test_non_truezero_not_converted(zero):
    d=fixture();d['zero_interpretation']=zero
    assert 'ZERO_IS_NOT_QUANTITATIVE_ABSENCE' in assess_censor_contract(d)['unresolved_or_blocking_reasons']

@pytest.mark.parametrize('field,value',[('DTL_number',1),('zero_interpretation',{}),('unit','invented'),('normalization',True),('raw_value','PRIVATE-RAW')])
def test_raw_numeric_unknown_rejected(field,value):
    d=fixture();d[field]=value
    with pytest.raises(ValueError) as e:assess_censor_contract(d)
    assert str(e.value)=='censoring contract rejected'

def test_contradictions():
    d=fixture();d['normalization']='not_applicable_verified'
    assert 'CONTRADICTORY_NORMALIZATION_SEMANTICS' in assess_censor_contract(d)['unresolved_or_blocking_reasons']
    d=fixture();d.update(zero_interpretation='below_DTL',DTL_policy='not_applicable_verified')
    assert 'CONTRADICTORY_DTL_SEMANTICS' in assess_censor_contract(d)['unresolved_or_blocking_reasons']

def test_omm12_remains_abstain():
    p=Path(__file__).resolve().parents[1]/'results/omm12_censor_semantics_metadata_20261010.json'
    r=load_censor_contract(p);assert r['status']=='ABSTAIN' and not r['C1_admitted']
    assert 'UNRESOLVED_ZERO_INTERPRETATION' in r['unresolved_or_blocking_reasons']

def test_cli_noecho(tmp_path,capsys):
    p=tmp_path/'c.json';p.write_text(json.dumps(fixture()))
    assert main(['check-censor-semantics',str(p)])==0
    p.write_text('{"raw":"PRIVATE-RAW"}')
    assert main(['check-censor-semantics',str(p)])==2
    out=capsys.readouterr();assert 'PRIVATE-RAW' not in out.out+out.err
