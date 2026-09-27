import json
from pathlib import Path

def test_pipeline_version_is_not_duplicate_biological_unit():
    d=json.loads((Path(__file__).resolve().parents[1]/'results/oral_column_identity.json').read_text())
    assert d['raw_ssu_columns']==d['nonzero_ssu_columns']==d['retained_columns']==111
    assert d['exact_retained_run_matches']==d['retained_selected_pipeline_5_0_analysis_records']==111
    assert d['analysis_versions_per_retained_run']=={'2':111}
    assert d['analysis_count']==222 and d['sample_count']==111
    assert d['inconsistent_sample_links_across_pipeline_versions']==0
    assert d['linked_sample_relationships']==d['unique_linked_sample_ids']==111
    assert d['matched_analysis_type_counts']=={'amplicon':111}
    assert sum(d['linked_sample_descriptions'].values())==111
    assert all(k.startswith(('saliva','dental plaque')) for k in d['linked_sample_descriptions'])
    assert d['linked_explicit_host_names']==d['linked_normalized_species']=={'Homo sapiens':111}
