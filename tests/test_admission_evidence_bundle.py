import json,shutil
from pathlib import Path
import pytest
from microtwin import admission_evidence_bundle as b
from microtwin.cli import main

@pytest.fixture
def root(tmp_path,monkeypatch):
    dest=tmp_path/'results';dest.mkdir()
    for n in b.FILES.values():shutil.copy(b.ROOT/'results'/n,dest/n)
    monkeypatch.setattr(b,'ROOT',tmp_path)
    return tmp_path

def test_roundtrip_and_no_overwrite(root):
    p=root/'receipt.json';b.create_receipt(p)
    d=json.loads(p.read_text());assert set(d['roles'])==set(b.FILES)
    assert 'literal' not in p.read_text() and not d['source_outcome_access']
    assert b.verify_receipt(p)['status']=='local_evidence_hashes_and_boundary_match'
    with pytest.raises(ValueError):b.create_receipt(p)

@pytest.mark.parametrize('role',list(b.FILES))
def test_byte_tamper(root,role):
    p=root/'receipt.json';b.create_receipt(p)
    f=root/'results'/b.FILES[role];f.write_bytes(f.read_bytes()+b'\n')
    with pytest.raises(ValueError,match='bundle rejected'):b.verify_receipt(p)

@pytest.mark.parametrize('attack',['missing','symlink','oversize','raw','status','extra','duplicate','unknown_schema'])
def test_reject_attack_no_echo(root,attack):
    p=root/'receipt.json';b.create_receipt(p)
    f=root/'results'/b.FILES['certificate']
    if attack=='missing':f.unlink()
    if attack=='symlink':
        raw=root/'private';raw.write_text('PRIVATE-RAW');f.unlink();f.symlink_to(raw)
    if attack=='oversize':f.write_bytes(b'x'*1_000_001)
    if attack=='raw':
        d=json.loads(f.read_text());d['raw_allowed_cells']=['PRIVATE-RAW'];f.write_text(json.dumps(d))
    if attack=='status':
        d=json.loads(f.read_text());d['quantitative_C1']='ADMITTED';f.write_text(json.dumps(d))
    if attack=='extra':
        d=json.loads(p.read_text());d['roles']['raw_quarantine']={'literal':'PRIVATE-RAW'};p.write_text(json.dumps(d))
    if attack=='duplicate':p.write_text('{"a":1,"a":2}')
    if attack=='unknown_schema':
        d=json.loads(p.read_text());d['schema']='PRIVATE-RAW';p.write_text(json.dumps(d))
    with pytest.raises(ValueError) as e:b.verify_receipt(p)
    assert str(e.value)=='admission evidence bundle rejected'

def test_cli_and_status_output_tamper(root,capsys):
    p=root/'receipt.json';assert main(['receipt-admission-evidence',str(p),'--evidence-dir',str(root/'results')])==0
    assert main(['verify-admission-evidence',str(p),'--evidence-dir',str(root/'results')])==0
    f=root/'results'/b.FILES['boundary_check'];f.write_text('{"secret":"PRIVATE-RAW"}')
    assert main(['verify-admission-evidence',str(p),'--evidence-dir',str(root/'results')])==2
    out=capsys.readouterr();assert 'PRIVATE-RAW' not in out.out+out.err

def test_synthetic_demo_portable_explicit_directory(tmp_path):
    from microtwin.admission_demo import create_demo
    evidence=tmp_path/'evidence';create_demo(evidence)
    receipt=tmp_path/'receipt.json'
    b.create_receipt(receipt,evidence_dir=evidence)
    assert b.verify_receipt(receipt,evidence_dir=evidence)['quantitative_admission'] is False
    with pytest.raises(ValueError):create_demo(evidence)

def test_metadata_path_no_scientific_dependency_imports(tmp_path):
    import subprocess,sys
    # -S disables site packages; explicitly expose source code only.
    script='''import sys
sys.path.insert(0,sys.argv[1])
from microtwin.admission_demo import create_demo
from microtwin.cli import main
from pathlib import Path
p=Path(sys.argv[2]);create_demo(p/'evidence')
assert main(['check-admission-boundary',str(p/'evidence/omm12_quarantine_certificate_20261010.json')])==0
assert main(['receipt-admission-evidence',str(p/'receipt.json'),'--evidence-dir',str(p/'evidence')])==0
assert main(['verify-admission-evidence',str(p/'receipt.json'),'--evidence-dir',str(p/'evidence')])==0
assert not any(m in sys.modules for m in ('numpy','pandas','scipy','torch','skbio'))
'''
    r=subprocess.run([sys.executable,'-S','-c',script,str(Path(__file__).resolve().parents[1]/'src'),str(tmp_path)],capture_output=True,text=True)
    assert r.returncode==0,r.stderr
