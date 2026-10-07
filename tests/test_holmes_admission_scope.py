import json
from pathlib import Path


def test_holmes_census_keeps_unresolved_population():
    r=json.loads(Path('results/holmes_scfa_metadata_census_20261007.json').read_text())
    assert r['row_count']==440 and r['distinct_PID']==36 and r['distinct_ID']==1
    assert r['missing_metadata']['Treatment']==27
    assert r['role']=='descriptive_source_admission_only'
    assert not r['outcome_values_retained'] and not r['numeric_outcomes_parsed']
    assert '28' not in str(r['distinct_PID'])


def test_overlap_not_identity_proof():
    r=json.loads(Path('results/holmes_baxter_accession_overlap_20261007.json').read_text())
    assert r['exact_sample_accession_overlap']==0
    assert r['person_identity_disjointness_verified'] is False
    assert max(r['response_bytes'].values())<100000


def test_report_role_and_no_posthoc_filter():
    t=Path('results/HOLMES_SCFA_SOURCE_ADMISSION_20261007.md').read_text()
    for text in ['not a discovery or prospective evaluation','Power is not computed','not a permitted automatic filter','remain unverified','Baxter remains parked','No fitting']:
        assert text in t
