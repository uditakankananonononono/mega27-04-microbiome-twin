import json
import pytest
from microtwin.prediction_losses import paired_prediction_losses
from microtwin.multimodel_leaderboard import freeze_comparator,compare_frozen_models


def files(tmp_path,prefix='v'):
    truth=tmp_path/(prefix+'truth.csv'); labels=tmp_path/(prefix+'labels.csv')
    truth.write_text('sample_id,A,B\ns1,0.8,0.2\ns2,0.2,0.8\n')
    labels.write_text(f'sample_id,subject_id,source_family\ns1,{prefix}a,{prefix}1\ns2,{prefix}b,{prefix}2\n')
    paths={}
    for name,body in [('twin','s1,0.7,0.3\ns2,0.3,0.7\n'),('prior','s1,0.5,0.5\ns2,0.5,0.5\n')]:
        p=tmp_path/(prefix+name+'.csv');p.write_text('sample_id,A,B\n'+body);paths[name]=p
    return truth,paths,labels


def test_direct_numeric_and_workflow(tmp_path):
    v=paired_prediction_losses(*files(tmp_path,'v'))
    assert v['loss_input']['errors']['twin']==pytest.approx([.1,.1])
    assert v['loss_input']['errors']['prior']==pytest.approx([.3,.3])
    s=freeze_comparator(v['loss_input']['errors'],v['loss_input']['families'],candidate='twin')
    t=paired_prediction_losses(*files(tmp_path,'t'))
    r=compare_frozen_models(s,t['loss_input']['errors'],t['loss_input']['families'],n_boot=100)
    assert not r['external_win_certified']
    assert r['primary_selected_comparator_statistic']['delta_candidate_minus_baseline']==pytest.approx(-.2)
    assert 's1' not in json.dumps(v['provenance'])


@pytest.mark.parametrize('bad',[
'sample_id,A,B\ns2,0.3,0.7\ns1,0.7,0.3\n',
'sample_id,B,A\ns1,0.3,0.7\ns2,0.7,0.3\n',
'sample_id,A,B\ns1,7,3\ns2,3,7\n',
'sample_id,A,B\ns1,nan,0.3\ns2,0.3,0.7\n',
'sample_id,A,B\ns1,-0.1,1.1\ns2,0.3,0.7\n',
'sample_id,A,A\ns1,0.7,0.3\ns2,0.3,0.7\n',
'sample_id,A,B\ns1,0.7,0.3\n',
'sample_id,A,B\ns1,0.7,0.3,0\ns2,0.3,0.7\n'])
def test_no_silent_repair(tmp_path,bad):
    truth,paths,labels=files(tmp_path);paths['twin'].write_text(bad)
    with pytest.raises(ValueError):paired_prediction_losses(truth,paths,labels)


def test_subject_cross_family(tmp_path):
    truth,paths,labels=files(tmp_path)
    labels.write_text('sample_id,subject_id,source_family\ns1,p,v1\ns2,p,v2\n')
    with pytest.raises(ValueError,match='multiple source'):paired_prediction_losses(truth,paths,labels)


def test_symlink_and_missing_model(tmp_path):
    truth,paths,labels=files(tmp_path)
    with pytest.raises(ValueError):paired_prediction_losses(truth,{'prior':paths['prior']},labels)
    link=tmp_path/'link.csv';link.symlink_to(paths['twin']);paths['twin']=link
    with pytest.raises(ValueError):paired_prediction_losses(truth,paths,labels)


def test_cli_privacy_and_existing_output(tmp_path,capsys):
    from microtwin.cli import main
    truth,paths,labels=files(tmp_path)
    mapping=tmp_path/'models.json';mapping.write_text(json.dumps({m:str(p) for m,p in paths.items()}))
    out=tmp_path/'losses.json'
    args=['prediction-losses',str(truth),'--models',str(mapping),'--labels',str(labels),'--out',str(out)]
    assert main(args)==0
    stdout=capsys.readouterr().out
    assert 's1' not in stdout and 'v1' not in stdout and 'loss_input' not in stdout
    assert json.loads(out.read_text())['loss_input']['errors']['twin']==pytest.approx([.1,.1])
    old=out.read_bytes();assert main(args)==2 and out.read_bytes()==old


def test_input_change_detected(tmp_path,monkeypatch):
    import microtwin.prediction_losses as module
    truth,paths,labels=files(tmp_path);original=module.bray_curtis
    def mutate(p,y):
        truth.write_text(truth.read_text()+'\n')
        return original(p,y)
    monkeypatch.setattr(module,'bray_curtis',mutate)
    with pytest.raises(ValueError,match='changed'):module.paired_prediction_losses(truth,paths,labels)


@pytest.mark.parametrize('role',['truth','prediction','labels'])
@pytest.mark.parametrize('kind',['unclosed','junk_after_quote','invalid_utf8'])
def test_malformed_records_rejected_without_private_labels(tmp_path,role,kind):
    from microtwin.prediction_losses import paired_prediction_losses
    truth=tmp_path/'truth.csv';truth.write_text('sample_id,A\ns1,1\n')
    a=tmp_path/'a.csv';a.write_text(truth.read_text())
    b=tmp_path/'b.csv';b.write_text(truth.read_text())
    labels=tmp_path/'labels.csv';labels.write_text('sample_id,subject_id,source_family\ns1,p1,f1\n')
    dest={'truth':truth,'prediction':a,'labels':labels}[role]
    if role=='labels':
        prefix=b'sample_id,subject_id,source_family\ns1,p1,';value=b'PRIVATE_FAMILY'
    else:
        prefix=b'sample_id,A\ns1,';value=b'1'
    tail={'unclosed':b'"'+value,'junk_after_quote':b'"'+value+b'"junk\n','invalid_utf8':b'\xff'+value+b'\n'}[kind]
    dest.write_bytes(prefix+tail)
    with pytest.raises(ValueError) as error:
        paired_prediction_losses(truth,{'a':a,'b':b},labels)
    assert str(error.value) in ('well-formed UTF-8 composition table required','well-formed UTF-8 label map required')
    assert 'PRIVATE' not in str(error.value)
