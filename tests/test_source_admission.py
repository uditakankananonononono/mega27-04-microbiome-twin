import json
from pathlib import Path
import pytest
from microtwin.source_admission import assess_source,assess_many
from scripts.source_admission_screen import run

def complete():
    return {'study':'synthetic','analysis_pagination_complete':True,
      'uniform_analysis_experiment_type':'amplicon','sample_pagination_complete':True,
      'old_column_to_analysis_mapped':True,'explicit_human_host_compatible':True,
      'independent_biological_family':True}

def test_all_metadata_complete_still_needs_manual_review():
    r=assess_source(complete())
    assert r['decision']=='metadata_ready_for_manual_review' and not r['final_external_benchmark_eligible']

@pytest.mark.parametrize('field,value',[('analysis_pagination_complete','unknown'),
   ('uniform_analysis_experiment_type','assembly'),('sample_pagination_complete',False),
   ('old_column_to_analysis_mapped','unknown'),('explicit_human_host_compatible',False),
   ('independent_biological_family','unknown')])
def test_any_failed_field_blocks(field,value):
    row=complete();row[field]=value;r=assess_source(row)
    assert r['decision']=='blocked' and [x['field'] for x in r['reasons']]==[field]

def test_missing_field_never_defaults_to_pass():
    row=complete();row.pop('old_column_to_analysis_mapped')
    assert assess_source(row)['decision']=='blocked'

def test_real_viewed_records_remain_unadmitted():
    d=run();assert d['candidate_records']==8 and d['blocked']==8
    assert d['metadata_ready_for_manual_review']==d['independent_external_benchmark_datasets']==0
    x={r['study']:r for r in d['records']}
    assert {'explicit_human_host_compatible','independent_biological_family'} <= {v['field'] for v in x['MGYS00006755']['reasons']}
    assert 'old_column_to_analysis_mapped' not in {v['field'] for v in x['MGYS00006755']['reasons']}
    assert {v['field'] for v in x['MGYS00002238']['reasons']}=={'independent_biological_family'}
    assert {v['field'] for v in x['MGYS00005154']['reasons']}=={'independent_biological_family'}

def test_duplicate_identity_rejected():
    with pytest.raises(ValueError,match='duplicate'):assess_many([complete(),complete()])
