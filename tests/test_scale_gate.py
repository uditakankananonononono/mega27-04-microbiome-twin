import pytest
from microtwin.scale_gate import scale_status


def test_unverified_rows_do_not_count_toward_millions():
    r=scale_status([{'accession':'A','independent_samples':2000000},
                    {'accession':'B','source_family':'family-b','independent_samples':100,'independence_verified':True,
                     'license_verified':True,'input_qc_passed':True,'source_hash_verified':True}])
    assert r['verified_datasets']==1 and r['verified_independent_samples']==100
    assert not r['foundation_scale_target_met']


def test_duplicate_verified_accession_rejected():
    row={'accession':'A','source_family':'family-a','independent_samples':10,'independence_verified':True,
         'license_verified':True,'input_qc_passed':True,'source_hash_verified':True}
    with pytest.raises(ValueError):scale_status([row,row])


def test_boolean_samples_and_targets_cannot_count_as_measurements():
    verified={'accession':'B','source_family':'family-b','independent_samples':True,'independence_verified':True,
              'license_verified':True,'input_qc_passed':True,'source_hash_verified':True}
    with pytest.raises(ValueError, match="sample count"):
        scale_status([verified])
    with pytest.raises(ValueError, match="scale targets"):
        scale_status([], foundation_samples=True)
    with pytest.raises(ValueError, match="scale targets"):
        scale_status([], target_min=1.2)


def test_malformed_record_fails_closed():
    with pytest.raises(ValueError, match="mappings"):
        scale_status([None])


def test_case_variant_verified_accessions_are_one_source():
    row={'accession':'PRJEB11419','source_family':'family-agp','independent_samples':10,'independence_verified':True,
         'license_verified':True,'input_qc_passed':True,'source_hash_verified':True}
    with pytest.raises(ValueError, match='unique'):
        scale_status([row, {**row,'accession':'prjeb11419'}])



def test_alias_accessions_cannot_double_count_one_family():
    row={'accession':'MGYS00006825','source_family':'PRJNA715245','independent_samples':500,
         'independence_verified':True,'license_verified':True,'input_qc_passed':True,'source_hash_verified':True}
    with pytest.raises(ValueError,match='source families must be unique'):
        scale_status([row,{**row,'accession':'MGYS00006862','source_family':' prjna715245 '}])
    with pytest.raises(ValueError,match='source_family required'):
        scale_status([{**row,'source_family':''}])
    r=scale_status([row])
    assert r['verified_datasets']==r['verified_biological_families']==1
    assert not r['foundation_scale_target_met']
