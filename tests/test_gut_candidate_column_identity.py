import json
from pathlib import Path

def test_400_selected_columns_not_965_independent_observations():
    d=json.loads((Path(__file__).resolve().parents[1]/'results/gut_candidate_column_identity.json').read_text())
    assert d['raw_ssu_columns']==d['exact_raw_run_matches']==529
    assert d['retained_columns']==d['exact_retained_run_matches']==400
    assert d['analysis_count']==965 and d['sample_count']==529
    assert d['pipeline_5_0_selected_analysis_records']==d['linked_sample_relationships']==d['unique_linked_sample_ids']==400
    assert d['current_analysis_versions_per_retained_run']=={'2':320,'1':80}
    assert d['cross_version_sample_link_conflicts']==0
    assert d['selected_analysis_type_counts']=={'amplicon':400}
    assert d['linked_explicit_host_names']==d['linked_normalized_species']=={'Homo sapiens':400}
    assert sum(d['linked_sample_descriptions'].values())==400
    assert not d['linked_explicit_collection_site_values']
    for typ,total in [('analyses',965),('samples',529)]:
        assert sum(p['items'] for p in d['api_pages'][typ])==total
        assert all(p['declared_total']==total for p in d['api_pages'][typ])
