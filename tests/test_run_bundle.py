import json
import pytest
from microtwin.cli import main

def run(tmp_path,manifest=True):
 t=tmp_path/'train.csv';t.write_text('sample_id,A,B\ns1,2,0\ns2,0,2\n');q=tmp_path/'query.csv';q.write_text('sample_id,A,B\nx1,1,1\n')
 b=dict(source_family='toy',material='stool',assay='16S',taxonomy_version='v1',processing_pipeline='toy',unit='counts')
 c=tmp_path/'contract.json';c.write_text(json.dumps(dict(train=b,query=b)));o=tmp_path/'out.csv';m=tmp_path/'receipt.json'
 args=['predict-checked',str(t),str(q),'--contracts',str(c),'--unit','counts','--source-id','toy','--processing-authorized','--out',str(o)]
 if manifest:args+=['--manifest',str(m)]
 return args,t,q,c,o,m

def test_roundtrip(tmp_path,capsys):
 args,t,q,c,o,m=run(tmp_path);assert main(args)==0
 obj=json.loads(m.read_text());assert obj['schema']=='microtwin.local-integrity.v1' and not obj['external_validation']
 assert 's1,2' not in m.read_text()
 assert main(['verify-bundle',str(m),'--train',str(t),'--query',str(q),'--contracts',str(c),'--prediction',str(o)])==0
 assert 'local_artifact_hashes_match' in capsys.readouterr().out

@pytest.mark.parametrize('role',['train','query','contracts','prediction'])
def test_tamper(tmp_path,role):
 args,t,q,c,o,m=run(tmp_path);assert main(args)==0
 files=dict(train=t,query=q,contracts=c,prediction=o);files[role].write_text(files[role].read_text()+'\n')
 assert main(['verify-bundle',str(m),'--train',str(t),'--query',str(q),'--contracts',str(c),'--prediction',str(o)])==2

def test_existing_manifest_no_output(tmp_path):
 args,t,q,c,o,m=run(tmp_path);m.write_text('KEEP');assert main(args)==2;assert not o.exists() and m.read_text()=='KEEP'

def test_invalid_manifest_schema(tmp_path):
 args,t,q,c,o,m=run(tmp_path);m.write_text('[]');assert main(['verify-bundle',str(m),'--train',str(t),'--query',str(q),'--contracts',str(c),'--prediction',str(o)])==2

def test_symlink_manifest(tmp_path):
 args,t,q,c,o,m=run(tmp_path);assert main(args)==0
 link=tmp_path/'link.json';link.symlink_to(m)
 assert main(['verify-bundle',str(link),'--train',str(t),'--query',str(q),'--contracts',str(c),'--prediction',str(o)])==2

def test_subject_map_receipt(tmp_path):
 args,t,q,c,o,m=run(tmp_path);s=tmp_path/'subjects.csv';s.write_text('sample_id,subject_id\ns1,a\ns2,b\n')
 assert main(args+['--subject-map',str(s)])==0
 verify=['verify-bundle',str(m),'--train',str(t),'--query',str(q),'--contracts',str(c),'--prediction',str(o)]
 assert main(verify)==2
 assert main(verify+['--subject-map',str(s)])==0
 s.write_text(s.read_text()+'\n');assert main(verify+['--subject-map',str(s)])==2
