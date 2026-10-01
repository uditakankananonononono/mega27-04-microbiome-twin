import json
import pytest
from microtwin.cli import main

def rows(n=20):
 return [dict(sample_id=f's{i}',source_family='F',subject_id='person1',collection_time=str(i),aliquot_group=f'aliquot{i}') for i in range(n)]

def test_repeated_time_not_independent_subjects(tmp_path,capsys):
 p=tmp_path/'m.json';r=rows();p.write_text(json.dumps({'16S':r,'metagenomics':r}))
 assert main(['check-multimodal',str(p)])==0
 obj=json.loads(capsys.readouterr().out);assert obj['aligned_common_samples']==20 and obj['submitted_subject_groups']==1
 assert obj['submitted_collection_times']==20 and not obj['biological_independence_verified'] and not obj['physical_aliquot_verified']
 assert 'person1' not in json.dumps(obj)

@pytest.mark.parametrize('field',['subject_id','source_family','collection_time','aliquot_group'])
def test_provenance_conflict(tmp_path,field):
 r=rows();q=[x.copy() for x in r];q[0][field]='wrong';p=tmp_path/'m.json';p.write_text(json.dumps({'16S':r,'metagenomics':q}));assert main(['check-multimodal',str(p)])==2

def test_insufficient_and_bad_shape(tmp_path):
 p=tmp_path/'m.json';p.write_text(json.dumps({'16S':rows(2),'metagenomics':rows(2)}));assert main(['check-multimodal',str(p)])==2
 p.write_text('[]');assert main(['check-multimodal',str(p)])==2

def test_same_subject_label_different_source_counted_separate_groups(tmp_path,capsys):
 r=rows(2);r[1]['source_family']='G';p=tmp_path/'m.json';p.write_text(json.dumps({'16S':r,'metagenomics':r}))
 assert main(['check-multimodal',str(p),'--min-paired','2'])==0
 obj=json.loads(capsys.readouterr().out);assert obj['submitted_subject_groups']==2 and obj['submitted_source_families']==2
