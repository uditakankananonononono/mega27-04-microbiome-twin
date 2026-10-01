import pandas as pd,pytest
from microtwin.benchmark_export import export_paired_report


def files(tmp_path):
 l=tmp_path/'l.csv';p=tmp_path/'p.csv'
 l.write_text('sample_id,subject_id,fold,prior_error,interaction_error\na,A,1,0.4,0.2\nb,B,2,0.5,0.4\n')
 p.write_text('sample_id,subject_id,fold,partition\na,A,1,test\nb,B,1,train\na,A,2,train\nb,B,2,test\n')
 return l,p

def test_valid_exact_grouped_report(tmp_path):
 l,p=files(tmp_path);r=export_paired_report(l,p,n_boot=10)
 assert r['n_samples']==r['n_subject_labels']==2
 assert r['predictive_dependence']['ecosystem_score']==pytest.approx(.35)
 assert not r['external_win_certified'] and r['reliability']['twin_reliability_index'] is None
 assert r['reliability']['components']['prediction_accuracy']['status']=='missing'

@pytest.mark.parametrize('case',['leak','wrong_fold','wrong_subject','negative','duplicate','blank'])
def test_bad_reports_rejected(tmp_path,case):
 l,p=files(tmp_path);d=pd.read_csv(l);m=pd.read_csv(p)
 if case=='leak':m['subject_id']='A';d['subject_id']='A'
 if case=='wrong_fold':d.loc[0,'fold']=2
 if case=='wrong_subject':d.loc[0,'subject_id']='C'
 if case=='negative':d.loc[0,'prior_error']=-1
 if case=='duplicate':d=pd.concat([d,d.iloc[:1]])
 if case=='blank':m.loc[0,'subject_id']=' '
 d.to_csv(l,index=False);m.to_csv(p,index=False)
 with pytest.raises(ValueError):export_paired_report(l,p,n_boot=10)

@pytest.mark.parametrize('boot',[-1,True,10001,1.5])
def test_bounded_bootstrap(tmp_path,boot):
 l,p=files(tmp_path)
 with pytest.raises(ValueError,match='n_boot'):export_paired_report(l,p,n_boot=boot)

def test_cli_export(tmp_path,capsys):
 import json
 from microtwin.cli import main
 l,p=files(tmp_path);assert main(['export-benchmark',str(l),str(p),'--n-boot','10'])==0
 r=json.loads(capsys.readouterr().out);assert r['status']=='submitted_loss_report_not_a_model_run'
