import json
from pathlib import Path
import pytest
from scripts.metadata_integrity_matrix import run

def test_known_metadata_conflict_and_unknowns_fail_closed():
    d=run();assert d['n_studies']==8
    x={r['study']:r for r in d['rows']}
    assert x['MGYS00006755']['explicit_human_host_compatible'] is False
    assert x['MGYS00006006']['uniform_analysis_experiment_type']=='assembly'
    assert x['MGYS00006795']['explicit_human_host_compatible']=='unknown'
    assert x['MGYS00000633']['analysis_pagination_complete']=='unknown'
    assert x['MGYS00006755']['old_column_to_analysis_mapped'] is True
    assert x['MGYS00002238']['old_column_to_analysis_mapped'] is True
    assert x['MGYS00005154']['old_column_to_analysis_mapped'] is True
    assert x['MGYS00006794']['old_column_to_analysis_mapped'] is True
    assert x['MGYS00006794']['human_gut_site_compatible'] is False
    assert x['MGYS00002238']['human_gut_site_compatible'] is False
    assert all(r['old_column_to_analysis_mapped']=='unknown' for r in d['rows'] if r['study'] not in ('MGYS00006755','MGYS00002238','MGYS00005154','MGYS00006794'))
    assert all(r['independent_biological_family']=='unknown' for r in d['rows'])

def test_missing_host_name_cannot_become_compatible(tmp_path):
    d=json.loads(Path('results/gut_analysis_metadata_crosswalk_partial.json').read_text())
    r=d['completed_rows'][0];r['sample_metadata_host_scientific_name_counts']={'Homo sapiens':r['sample_count']-1}
    r['samples_without_usable_host_name']=1;r['human_normalized_vs_nonhuman_host_name_conflict_samples']=0
    f=tmp_path/'partial.json';f.write_text(json.dumps(d))
    assert next(x for x in run(f)['rows'] if x['study']==r['study'])['explicit_human_host_compatible']=='unknown'
