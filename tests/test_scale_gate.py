import pytest
from microtwin.scale_gate import scale_status


def test_unverified_rows_do_not_count_toward_millions():
    r=scale_status([{'accession':'A','independent_samples':2000000},
                    {'accession':'B','independent_samples':100,'independence_verified':True,
                     'license_verified':True,'input_qc_passed':True,'source_hash_verified':True}])
    assert r['verified_datasets']==1 and r['verified_independent_samples']==100
    assert not r['foundation_scale_target_met']


def test_duplicate_verified_accession_rejected():
    row={'accession':'A','independent_samples':10,'independence_verified':True,
         'license_verified':True,'input_qc_passed':True,'source_hash_verified':True}
    with pytest.raises(ValueError):scale_status([row,row])


def test_boolean_samples_and_targets_cannot_count_as_measurements():
    verified={'accession':'B','independent_samples':True,'independence_verified':True,
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
