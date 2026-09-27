import json
from pathlib import Path


def test_crosswalk_aggregates_only_complete_source_pages():
    files=sorted(Path('results').glob('gut_analysis_metadata_crosswalk_MGYS*.json'))
    assert len(files)==7
    for f in files:
        data=json.loads(f.read_text());r=data['rows'][0]
        assert r['analysis_count']==sum(r['experiment_type_analysis_counts'].values())
        assert r['sample_count']==sum(r['normalized_sample_species_counts'].values())
        assert r['analysis_count']==sum(p['items'] for p in r['analysis_pages'])
        assert r['sample_count']==sum(p['items'] for p in r['sample_pages'])
        assert all(len(p['response_sha256'])==64 for p in r['analysis_pages']+r['sample_pages'])
        assert 'sample_id' not in str(r).lower()
    animal=json.loads(Path('results/gut_analysis_metadata_crosswalk_MGYS00006755.json').read_text())['rows'][0]
    assert animal['human_normalized_vs_nonhuman_host_name_conflict_samples']==83
    assert animal['experiment_type_analysis_counts']=={'amplicon':83}
    assembly=json.loads(Path('results/gut_analysis_metadata_crosswalk_MGYS00006006.json').read_text())['rows'][0]
    assert assembly['experiment_type_analysis_counts']=={'assembly':457}
    assert 'MGYS00000633' not in [json.loads(f.read_text())['rows'][0]['study'] for f in files]
