from microtwin.mirror_guard import validate_external_accessions


def test_exact_mirror_excluded_but_new_is_only_candidate():
    r=validate_external_accessions([{'study_id':550,'ebi_accession':'ERP021896'},
                                    {'study_id':999,'ebi_accession':'ERPNEW'}],['ERP021896'])
    assert r['excluded_exact_mirror']==1
    assert r['independence_verified']==0
    assert r['records'][1]['status']=='candidate_only_near_duplicate_unchecked'
