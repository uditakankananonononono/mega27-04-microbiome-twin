import json
import pytest
from microtwin.cli import main


def fixtures(tmp_path):
    v=tmp_path/'validation.json'; t=tmp_path/'test.json'; s=tmp_path/'selection.json'
    v.write_text(json.dumps({'errors':{'twin':[.3,.3],'prior':[.2,.2],'cnode':[.25,.25]},'families':['v1','v2']}))
    t.write_text(json.dumps({'errors':{'twin':[.1,.1],'prior':[.3,.3],'cnode':[.05,.05]},'families':['t1','t2']}))
    return v,t,s


def test_end_to_end(tmp_path,capsys):
    v,t,s=fixtures(tmp_path)
    assert main(['freeze-comparator',str(v),'--candidate','twin','--out',str(s)])==0
    assert json.loads(capsys.readouterr().out)['selected_comparator']=='prior'
    assert main(['compare-models',str(t),'--selection',str(s),'--n-boot','100'])==0
    r=json.loads(capsys.readouterr().out)
    assert r['selected_comparator']=='prior' and len(r['input_sha256'])==2
    assert not r['external_win_certified']
    assert r['primary_selected_comparator_statistic']['ci95_study_bootstrap']==pytest.approx([-.2,-.2])
    assert main(['freeze-comparator',str(v),'--candidate','twin','--out',str(s)])==2


@pytest.mark.parametrize('fault',['extra','invalid','overlap','missingmodel','symlink','huge'])
def test_refusal(tmp_path,capsys,fault):
    v,t,s=fixtures(tmp_path)
    assert main(['freeze-comparator',str(v),'--candidate','twin','--out',str(s)])==0
    data=json.loads(t.read_text())
    if fault=='extra':data['clinical_use']=True
    if fault=='overlap':data['families'][0]='v1'
    if fault=='missingmodel':del data['errors']['cnode']
    t.write_text(json.dumps(data))
    if fault=='invalid':t.write_text('{bad')
    if fault=='huge':t.write_text(' '*1_000_001)
    if fault=='symlink':
        link=tmp_path/'link.json';link.symlink_to(t);t=link
    assert main(['compare-models',str(t),'--selection',str(s)])==2


def test_existing_selection_preserved(tmp_path):
    v,t,s=fixtures(tmp_path);s.write_text('KEEP')
    assert main(['freeze-comparator',str(v),'--candidate','twin','--out',str(s)])==2
    assert s.read_text()=='KEEP'


def test_compare_stdout_never_echoes_family_labels(tmp_path,capsys):
    v,t,s=fixtures(tmp_path)
    data=json.loads(t.read_text());data['families']=['PRIVATE_FAMILY_A','PRIVATE_FAMILY_B'];t.write_text(json.dumps(data))
    assert main(['freeze-comparator',str(v),'--candidate','twin','--out',str(s)])==0
    capsys.readouterr()
    assert main(['compare-models',str(t),'--selection',str(s),'--n-boot','100'])==0
    text=capsys.readouterr().out
    assert 'PRIVATE_FAMILY_' not in text and 'study_deltas' not in text
    assert json.loads(text)['primary_selected_comparator_statistic']['delta_candidate_minus_baseline']==pytest.approx(-.2)
