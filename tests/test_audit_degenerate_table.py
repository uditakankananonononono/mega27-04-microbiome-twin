from scripts.audit_degenerate_table import run

def test_known_zero_median_table_reproduces_dimensions():
    x=run();a=x['aggregates']
    assert a['analyzed_samples']==135 and a['analyzed_taxa']==3
    assert a['archived_median_prior']==a['archived_median_interaction']==0
    assert len(x['source_sha256'])==64
