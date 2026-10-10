import copy,json
from pathlib import Path
import pytest
from microtwin.admission_boundary import check_boundary,load_boundary
from microtwin.cli import main
ROOT=Path(__file__).resolve().parents[1]
CERT=ROOT/'results/omm12_quarantine_certificate_20261010.json'

def fixture():return json.loads(CERT.read_text())

def test_real_certificate_preserves_boundary():
    r=load_boundary(CERT)
    assert r['status']=='boundary_consistent_not_authenticated'
    assert r['quantitative_C1']=='NOT_ADMITTED_LOCKED'
    assert r['structural_C1']=='ADMITTED_DOCUMENTARY_REPRESENTATION_COUNTS_ONLY'
    assert not r['quantitative_admitted'] and not r['eligible_untouched_holdout']
    assert not r['can_auto_claim_win']
    assert r['C2']=='BLOCKED' and r['C3']=='NOT_PROPOSED' and r['useful_win']=='NOT_TESTED'

@pytest.mark.parametrize('field,value',[
 ('protocol','new'),('quantitative_C1','ADMITTED'),('C2','ADMITTED'),('C3','VALIDATED'),
 ('useful_win',True),('zero_semantics','KNOWN'),('source_family','UNTOUCHED'),
 ('stage_B','PASS'),('selected_rows',True),('allowed_cells',2663),
 ('issues',[{'literal':'PRIVATE-RAW'}]),('source_sha256',{}),('parent_decision_at','PRIVATE-RAW'),
 ('representation_counts',{'AMBIGUOUS_ZERO':995,'NUMERIC_REPRESENTATION_VALID':1668}),
 ('representation_counts',{'AMBIGUOUS_ZERO':995,'NUMERIC_REPRESENTATION_VALID':True})])
def test_status_and_count_attacks_rejected(field,value):
    d=fixture();d[field]=value
    with pytest.raises(ValueError) as e:check_boundary(d)
    assert str(e.value)=='admission boundary certificate rejected'

@pytest.mark.parametrize('change',['extra','missing','nested','address','row_duplicate','key_duplicate','order','s1new'])
def test_no_raw_payload_or_bad_manifest(change):
    d=fixture()
    if change=='extra':d['raw_allowed_cells']=[{'literal':'PRIVATE-RAW'}]
    if change=='missing':del d['C2']
    if change=='nested':d['manifest'][0]['literal']='PRIVATE-RAW'
    if change=='address':d['manifest'][0]['addresses'][0]='N2'
    if change=='row_duplicate':d['manifest'][1]['addresses']=copy.deepcopy(d['manifest'][0]['addresses'])
    if change=='key_duplicate':d['manifest'][1]['sample_key']=d['manifest'][0]['sample_key']
    if change=='order':d['manifest'][0]['addresses'].reverse()
    if change=='s1new':d['manifest'][0]['sample_key']='OMM12_S1new_APF_W1'
    with pytest.raises(ValueError) as e:check_boundary(d)
    assert 'PRIVATE-RAW' not in str(e.value)

@pytest.mark.parametrize('raw',[b'{"private":"PRIVATE-RAW"}',b'{"a":1,"a":2}',b'{"a":NaN}',b'not-json PRIVATE-RAW',b'\xff',b'x'*1_000_001])
def test_loader_safe_failures(tmp_path,raw):
    p=tmp_path/'bad.json';p.write_bytes(raw)
    with pytest.raises(ValueError) as e:load_boundary(p)
    assert str(e.value)=='admission boundary certificate rejected'

def test_cli_real_and_private_failure(tmp_path,capsys):
    assert main(['check-admission-boundary',str(CERT)])==0
    out=capsys.readouterr();assert 'NOT_ADMITTED_LOCKED' in out.out
    bad=tmp_path/'bad.json';bad.write_text('{"secret":"PRIVATE-RAW"}')
    assert main(['check-admission-boundary',str(bad)])==2
    out=capsys.readouterr();assert not out.out and 'PRIVATE-RAW' not in out.err
