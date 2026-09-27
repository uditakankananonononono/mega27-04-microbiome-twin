from scripts.mgnify_assay_descriptive import run

def test_assay_strata_preserve_original_bh_calls():
    r=run()
    assert r['all']['tables']==160 and r['all']['original_160_BH_interaction_wins']==121
    assert sum(v['tables'] for v in r['strata'].values())==160
    assert sum(v['original_160_BH_interaction_wins'] for v in r['strata'].values())==121
    assert 'not certified amplicon' in r['limits']
