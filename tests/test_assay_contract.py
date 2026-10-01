import pytest
from microtwin.assay_contract import assess_measurement_contract

def base():return dict(source_family='RR5',material='feces',assay='V4',taxonomy_version='silva',processing_pipeline='DADA2',unit='relative_abundance')

def test_equal_contract_is_not_external_validation():
 r=assess_measurement_contract(base(),base());assert r['measurement_fields_match'] and not r['transfer_eligible'];assert not r['individual_twin_eligible']

@pytest.mark.parametrize('key,value',[('material','oral'),('assay','shotgun'),('taxonomy_version','mpa4'),('processing_pipeline','MetaPhlAn'),('unit','counts')])
def test_measurement_changes_abstain(key,value):
 q=base();q[key]=value;r=assess_measurement_contract(base(),q);assert r['status']=='abstain_measurement_mismatch' and key in r['mismatched_fields']

def test_family_change_is_not_proof_of_independence():
 q=base();q['source_family']='RR6';r=assess_measurement_contract(base(),q);assert r['measurement_fields_match'] and r['independent_source_family_claimed'];assert not r['transfer_eligible']

@pytest.mark.parametrize('value',[None,{},'unknown',dict(assay='V4')])
def test_incomplete_rejected(value):
 with pytest.raises(ValueError):assess_measurement_contract(base(),value)

def test_bad_unit_rejected():
 q=base();q['unit']='percent';
 with pytest.raises(ValueError,match='unit'):assess_measurement_contract(base(),q)

def test_cli_measurement_mismatch_returns_failure(tmp_path,capsys):
 import json
 from microtwin.cli import main
 q=base();q['assay']='shotgun';p=tmp_path/'contracts.json';p.write_text(json.dumps({'train':base(),'query':q}))
 assert main(['check-assays',str(p)])==2
 r=json.loads(capsys.readouterr().out);assert not r['transfer_eligible']

def test_cli_bad_shape_returns_failure(tmp_path,capsys):
 from microtwin.cli import main
 p=tmp_path/'contracts.json';p.write_text('[]');assert main(['check-assays',str(p)])==2
