import json
from pathlib import Path
import pytest
from microtwin.comparator_capability import screen_comparators,load_comparators
from microtwin.cli import main

def fixture():
    m=dict(task='removal_response',output='normalized_qPCR_disturbance',horizon='day4',input_information=['preintervention_composition'],capability='implemented',adapter='verified',tuning_trials=10,failure_policy='retain_all')
    return dict(schema='microtwin.comparator-capability.metadata.v1',task=m['task'],output=m['output'],horizon='day4',allowed_information=m['input_information'],protocol_timing='frozen_before_outcomes',comparator_selection='frozen_before_test',test_source_status='untouched_independence_reviewed',models=[dict(m,role=r) for r in ['candidate','comparator']])

def test_ready_still_not_fairness_or_win():
    r=screen_comparators(fixture());assert r['status']=='DECLARED_FAIR_PLAN_READY_FOR_MANUAL_REVIEW'
    assert not any(r[k] for k in ['fairness_source_verified','losses_consumed','external_benchmark_eligible','win_certified'])

@pytest.mark.parametrize('field,value,reason',[
 ('tuning_trials',20,'UNEQUAL_DECLARED_TUNING_BUDGET'),('failure_policy','drop_failures','FAILED_RUNS_NOT_PRESERVED'),
 ('capability','unsupported','COMPARATOR_OR_CANDIDATE_CAPABILITY_UNSUPPORTED_OR_UNKNOWN'),('adapter','missing','ADAPTER_MISSING_OR_UNKNOWN'),
 ('horizon','day20','NOT_SAME_TASK_OUTPUT_HORIZON'),('input_information',['strain_traits'],'UNEQUAL_INFORMATION_SET')])
def test_model_fairness_blocks(field,value,reason):
    d=fixture();d['models'][0][field]=value;assert reason in screen_comparators(d)['blockers']

@pytest.mark.parametrize('field,value,reason',[('protocol_timing','retrospective','PROTOCOL_NOT_PROSPECTIVELY_FROZEN'),('comparator_selection','retrospective','COMPARATOR_SELECTION_NOT_FROZEN_BEFORE_TEST'),('test_source_status','exposed','TEST_SOURCE_EXPOSED_OR_UNKNOWN')])
def test_frozen_and_holdout_blocks(field,value,reason):
    d=fixture();d[field]=value;assert reason in screen_comparators(d)['blockers']

@pytest.mark.parametrize('field,value',[('losses',[1]),('role','other'),('tuning_trials',True),('capability',{}),('raw','PRIVATE-RAW')])
def test_raw_and_unknown_noecho(field,value):
    d=fixture();d['models'][0][field]=value
    with pytest.raises(ValueError) as e:screen_comparators(d)
    assert str(e.value)=='comparator capability metadata rejected'

def test_omm12_blocked():
    p=Path(__file__).resolve().parents[1]/'results/omm12_comparator_plan_metadata_20261010.json'
    r=load_comparators(p);assert r['status']=='BLOCKED'
    assert 'TEST_SOURCE_EXPOSED_OR_UNKNOWN' in r['blockers'] and not r['win_certified']

def test_cli_noecho(tmp_path,capsys):
    p=tmp_path/'p.json';p.write_text(json.dumps(fixture()))
    assert main(['check-comparator-capability',str(p)])==0
    p.write_text('{"raw":"PRIVATE-RAW"}')
    assert main(['check-comparator-capability',str(p)])==2
    assert 'PRIVATE-RAW' not in capsys.readouterr().err
