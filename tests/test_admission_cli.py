import json
from microtwin.cli import main

def test_viewed_eight_blocked_and_no_raw_metadata_leaks(capsys):
    rc=main(['screen-sources','results/metadata_integrity_matrix.json'])
    out=capsys.readouterr()
    assert rc==2
    d=json.loads(out.out)
    assert d['candidate_records']==d['blocked']==8
    assert not d['independent_external_benchmark_datasets']
    assert 'missing_host_name_samples' not in out.out

def test_synthetic_ready_still_not_final_and_redacts_extras(tmp_path,capsys):
    x={'study':'synthetic','analysis_pagination_complete':True,
       'uniform_analysis_experiment_type':'amplicon','sample_pagination_complete':True,
       'old_column_to_analysis_mapped':True,'explicit_human_host_compatible':True,
       'human_gut_site_compatible':True,'independent_biological_family':True,
       'sample_id':'PRIVATE-FAKE-SAMPLE','abundance':[1,2,3]}
    p=tmp_path/'rows.json';p.write_text(json.dumps({'n_studies':1,'rows':[x]}))
    assert main(['screen-sources',str(p)])==0
    o=capsys.readouterr().out;d=json.loads(o)
    assert d['records'][0]['decision']=='metadata_ready_for_manual_review'
    assert not d['records'][0]['final_external_benchmark_eligible']
    assert 'PRIVATE-FAKE-SAMPLE' not in o and 'abundance' not in o

def test_invalid_shapes_and_duplicate_ids(tmp_path,capsys):
    for item in ({'n_studies':2,'rows':[]},{'n_studies':1,'rows':{}},
                 {'n_studies':2,'rows':[{'study':'x'},{'study':'x'}]}):
        p=tmp_path/'bad.json';p.write_text(json.dumps(item))
        assert main(['screen-sources',str(p)])==2
        assert 'cannot screen source metadata' in capsys.readouterr().err

def test_size_bound(tmp_path,capsys):
    p=tmp_path/'large.json';p.write_text(' '*1_000_001)
    assert main(['screen-sources',str(p)])==2
    assert 'oversized' in capsys.readouterr().err
