import pytest
from microtwin.multimodal import assess_modalities


def test_only_exact_pairing_counts():
    r=assess_modalities({'16S':['a','b','c'],'metabolomics':['b','c','d']},min_paired=2)
    assert r['paired_sample_ids']==['b','c'] and r['status']=='paired_metadata_candidate'
    assert assess_modalities({'16S':['a'],'metabolomics':['b']},min_paired=1)['paired_samples']==0


def test_duplicate_sample_ids_fail():
    with pytest.raises(ValueError):assess_modalities({'16S':['a','a']})
