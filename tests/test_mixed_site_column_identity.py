import json
from pathlib import Path

def test_exact_old_columns_link_to_structured_skin_metadata():
    d=json.loads((Path(__file__).resolve().parents[1]/'results/mixed_site_column_identity.json').read_text())
    assert d['raw_ssu_columns']==d['nonzero_ssu_columns']==d['retained_columns']==184
    assert d['exact_retained_run_matches']==d['selected_pipeline_5_0_analyses']==184
    assert d['retained_run_analysis_version_multiplicity']=={'1':184}
    assert d['linked_sample_relationships']==d['unique_linked_sample_ids']==184
    assert d['linked_environment_material']=={'UBERON:0002097':184}
    assert d['linked_environment_feature']=={'ENVO:2100003':184}
    assert d['ontology']['material']['label']=='skin of body'
    assert d['ontology']['feature']['label']=='skin environment'
    assert not d['linked_explicit_host_names']
    assert d['linked_normalized_species']=={'Homo sapiens':184}
    assert sum(d['linked_sample_description_counts'].values())==184
