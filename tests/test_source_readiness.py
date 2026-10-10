import json,shutil
from pathlib import Path
import pytest
from microtwin.source_readiness import packet
from microtwin.admission_evidence_bundle import FILES
from microtwin.cli import main
ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture
def directory(tmp_path):
    config=json.loads((ROOT/'results/readiness_inputs.json').read_text())
    for n in set(config['roles'].values())|set(FILES.values())|{'readiness_inputs.json'}:shutil.copy(ROOT/'results'/n,tmp_path/n)
    return tmp_path

def test_real_packet_no_masking(directory):
    r=packet(directory);assert r['status']=='BLOCKED'
    assert not r['domains']['boundary']['blocking'] and not r['domains']['evidence_receipt']['blocking']
    assert all(r['domains'][d]['blocking'] for d in ['design','lineage','semantics','fairness'])
    assert r['quantitative_C1']=='NOT_ADMITTED_LOCKED' and not r['auto_admission']
    assert 'mouse' not in json.dumps(r) and not r['outcomes_consumed']

@pytest.mark.parametrize('attack',['extra','missing','path','raw','duplicate','unknown'])
def test_bad_inputs_no_echo(directory,attack):
    p=directory/'readiness_inputs.json';d=json.loads(p.read_text())
    if attack=='extra':d['roles']['raw']='PRIVATE-RAW.json'
    if attack=='missing':del d['roles']['semantics']
    if attack=='path':d['roles']['lineage']='../private.json'
    if attack=='duplicate':d['roles']['lineage']=d['roles']['design']
    if attack=='unknown':d['schema']='PRIVATE-RAW'
    if attack=='raw':
        f=directory/d['roles']['semantics'];x=json.loads(f.read_text());x['raw']='PRIVATE-RAW';f.write_text(json.dumps(x))
    p.write_text(json.dumps(d))
    with pytest.raises(ValueError) as e:packet(directory)
    assert str(e.value)=='source readiness metadata packet rejected'

def test_cli_blocked(directory,capsys):
    assert main(['source-readiness',str(directory)])==2
    r=json.loads(capsys.readouterr().out);assert r['status']=='BLOCKED'

def test_all_consistent_declarations_manual_review_only(tmp_path):
    import runpy
    from microtwin.admission_demo import create_demo
    from microtwin.admission_evidence_bundle import create_receipt
    create_demo(tmp_path/'evidence');base=tmp_path/'evidence'
    fixtures={r:runpy.run_path(str(ROOT/'tests'/n))['fixture']() for r,n in [('design','test_nested_perturbation_design.py'),('lineage','test_specimen_lineage.py'),('semantics','test_censor_contract.py'),('fairness','test_comparator_capability.py')]}
    config=json.loads((ROOT/'results/readiness_inputs.json').read_text())
    for role,obj in fixtures.items():(base/config['roles'][role]).write_text(json.dumps(obj))
    (base/'readiness_inputs.json').write_text(json.dumps(config))
    create_receipt(base/config['roles']['evidence_receipt'],evidence_dir=base)
    r=packet(base)
    assert r['status']=='DECLARATIONS_READY_FOR_MANUAL_REVIEW'
    assert not r['auto_admission'] and not r['scientific_goals_completed']
    assert r['quantitative_C1']=='NOT_ADMITTED_LOCKED'
    # One domain's failure must block despite five passing domains.
    fixtures['semantics']['zero_interpretation']='unknown'
    (base/config['roles']['semantics']).write_text(json.dumps(fixtures['semantics']))
    assert packet(base)['status']=='BLOCKED'
