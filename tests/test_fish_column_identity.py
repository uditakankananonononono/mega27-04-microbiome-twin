import json
from pathlib import Path

def test_fish_snapshot_exact_linkage_invariants():
    x=json.loads((Path(__file__).resolve().parents[1]/'results/fish_column_identity.json').read_text())
    assert x['raw_ssu_columns']==150 and x['nonzero_ssu_columns']==142
    assert x['retained_audit_columns']==135
    assert x['exact_assembly_matches_retained']+x['unmatched_retained']==135
    assert x['exact_assembly_matches_retained']==x['linked_retained_samples']==x['unique_linked_retained_samples']
    for typ in ('analyses','samples'):
        assert sum(p['items'] for p in x['api_pages'][typ])==x['analysis_count' if typ=='analyses' else 'sample_count']
