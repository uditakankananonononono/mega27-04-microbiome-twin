import json
from pathlib import Path

def test_exact_83_run_column_host_conflict_snapshot():
    d=json.loads((Path(__file__).resolve().parents[1]/'results/conflicted_host_column_identity.json').read_text())
    assert d['raw_columns']==d['nonzero_columns']==d['retained_columns']==83
    assert d['exact_run_matches_retained']==d['linked_retained_samples']==d['unique_linked_retained_samples']==83
    assert d['matched_retained_analysis_types']=={'amplicon':83}
    assert sum(d['linked_retained_explicit_host_name_counts'].values())==83
    assert d['linked_retained_normalized_species_counts']=={'Homo sapiens':83}
    assert d['linked_retained_explicit_nonhuman_vs_normalized_human_conflicts']==83
    assert d['unlinked_retained_matches']==0
    for k in ('analyses','samples'):
        assert d['api_pages'][k]['count']==d['api_pages'][k]['declared_total']==83
