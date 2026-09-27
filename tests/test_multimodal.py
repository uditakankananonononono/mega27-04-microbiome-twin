import pytest
from microtwin.multimodal import assess_modalities


def test_only_exact_pairing_counts():
    r=assess_modalities({'16S':['a','b','c'],'metabolomics':['b','c','d']},min_paired=2)
    assert r['paired_sample_ids']==['b','c'] and r['status']=='paired_metadata_candidate'
    assert assess_modalities({'16S':['a'],'metabolomics':['b']},min_paired=1)['paired_samples']==0


def test_duplicate_sample_ids_fail():
    with pytest.raises(ValueError):assess_modalities({'16S':['a','a']})


def test_normalized_ids_do_not_create_false_pairing_or_duplicates():
    r=assess_modalities({'16S':['  a  '], 'metabolomics':['a']}, min_paired=1)
    assert r['paired_sample_ids']==['a']
    with pytest.raises(ValueError, match='unique'):
        assess_modalities({'16S':['a', ' a ']})
    with pytest.raises(ValueError, match='positive integer'):
        assess_modalities({'16S':['a']}, min_paired=True)


def test_single_modality_never_reports_paired_candidate():
    r=assess_modalities({'16S':['one','two']},min_paired=1)
    assert r['status']=='insufficient_paired_samples'


def test_strict_alignment_needs_two_modalities_and_agreeing_provenance():
    from microtwin.multimodal import assess_strict_alignment
    def row(s,**kwargs):
        x={'sample_id':s,'source_family':'family-a','subject_id':'person-a',
           'collection_time':'day-0','aliquot_group':'aliquot-a'}
        x.update(kwargs);return x
    same={'16S':[row('s1')],'metabolomics':[row('s1')]}
    r=assess_strict_alignment(same,min_paired=1)
    assert r['status']=='metadata_aligned_candidate' and r['aligned_common_samples']==1
    assert not r['physical_aliquot_verified'] and not r['biological_independence_verified']
    assert 's1' not in str(r)
    assert 'sha256' not in str(r) and 'hash' not in str(r)
    with pytest.raises(ValueError,match='two known'):
        assess_strict_alignment({'16S':[row('s1')]},min_paired=1)
    for key in ('source_family','subject_id','collection_time','aliquot_group'):
        bad={'16S':[row('s1')],'metabolomics':[row('s1',**{key:'different'})]}
        with pytest.raises(ValueError,match='conflict'):
            assess_strict_alignment(bad,min_paired=1)
    with pytest.raises(ValueError,match='duplicate'):
        assess_strict_alignment({'16S':[row('s1'),row('s1')],'metabolomics':[row('s1')]},min_paired=1)
