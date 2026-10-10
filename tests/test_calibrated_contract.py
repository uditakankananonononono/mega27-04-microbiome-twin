import json
import pytest
from microtwin.cli import main
from microtwin.local_calibrated_predict import predict_with_radius

def inputs(tmp_path):
 t=tmp_path/'t.tsv';t.write_text('sample_id\tA\tB\nt1\t8\t2\nt2\t4\t6\n')
 c=tmp_path/'c.tsv';c.write_text('sample_id\tA\tB\n'+''.join(f'c{i}\t3\t7\n' for i in range(20)))
 q=tmp_path/'q.tsv';q.write_text('sample_id\tA\tB\nq1\t1\t1\n')
 b=dict(source_family='toy',material='stool',assay='16S',taxonomy_version='v1',processing_pipeline='toy',unit='counts')
 f=tmp_path/'contracts.json';f.write_text(json.dumps({n:b.copy() for n in ('train','calibration','query')}));return t,c,q,f

def test_contract_pass_keeps_honest_radius(tmp_path):
 t,c,q,f=inputs(tmp_path);_,r=predict_with_radius(t,c,q,unit='counts',source_id='toy',processing_authorized=True,contracts=f)
 assert r['measurement_contract_status']=='matched_submitted_labels_only' and r['uncertainty']['radius']==pytest.approx(.3)
 assert not r['uncertainty']['same_source_and_assay_proof'] and not r['external_validation']

@pytest.mark.parametrize('role,field',[(r,f) for r in ('calibration','query') for f in ('assay','material','taxonomy_version','processing_pipeline','source_family','unit')])
def test_mismatch_no_cli_output(tmp_path,role,field):
 t,c,q,f=inputs(tmp_path);obj=json.loads(f.read_text());obj[role][field]='different' if field!='unit' else 'relative_abundance';f.write_text(json.dumps(obj));o=tmp_path/'o.csv'
 with pytest.raises(SystemExit):main(['predict-calibrated-checked',str(t),str(c),str(q),'--contracts',str(f),'--unit','counts','--source-id','toy','--processing-authorized','--out',str(o)])
 assert not o.exists()

def test_strict_cli_pass(tmp_path,capsys):
 t,c,q,f=inputs(tmp_path);o=tmp_path/'o.csv';assert main(['predict-calibrated-checked',str(t),str(c),str(q),'--contracts',str(f),'--unit','counts','--source-id','toy','--processing-authorized','--out',str(o)])==0
 assert json.loads(capsys.readouterr().out)['contract_sha256']

def test_legacy_explicit_unverified(tmp_path):
 t,c,q,f=inputs(tmp_path);_,r=predict_with_radius(t,c,q,unit='counts',source_id='toy',processing_authorized=True)
 assert r['measurement_contract_status']=='unverified_legacy_no_contract'


@pytest.mark.parametrize('kind',['nested_duplicate','role_duplicate','malformed','invalid_utf8'])
def test_ambiguous_contracts_fail_private_safe_without_output(tmp_path,kind,capsys):
 t,c,q,f=inputs(tmp_path)
 raw=f.read_bytes()
 if kind=='nested_duplicate':raw=raw.replace(b'"assay": "16S"',b'"assay": "PRIVATE_ASSAY", "assay": "16S"',1)
 elif kind=='role_duplicate':raw=raw[:-1]+b',"train":'+json.dumps(json.loads(raw)['train']).encode()+b'}'
 elif kind=='malformed':raw=b'{"PRIVATE_FIELD":'
 else:raw=b'{"PRIVATE_FIELD":"\xff"}'
 f.write_bytes(raw)
 with pytest.raises(ValueError) as error:
  predict_with_radius(t,c,q,unit='counts',source_id='toy',processing_authorized=True,contracts=f)
 assert str(error.value)=='contract JSON must be well-formed UTF-8 with unique fields'
 assert 'PRIVATE' not in str(error.value)
 for route,args in [('predict-checked',[str(t),str(q)]),('predict-calibrated-checked',[str(t),str(c),str(q)])]:
  out=tmp_path/(route+'.csv')
  argv=[route,*args,'--contracts',str(f),'--unit','counts','--source-id','toy','--processing-authorized','--out',str(out)]
  if route=='predict-checked':
   assert main(argv)==2
   err=capsys.readouterr().err
   assert 'well-formed UTF-8 with unique fields' in err and 'PRIVATE' not in err
  else:
   with pytest.raises(SystemExit,match='well-formed UTF-8 with unique fields'):main(argv)
  assert not out.exists()
