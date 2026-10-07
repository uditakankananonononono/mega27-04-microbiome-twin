import importlib.util
import io
import json
from pathlib import Path
import pytest


def load():
    spec=importlib.util.spec_from_file_location('rs_census','scripts/resistant_starch_metadata_census.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample(acc,phase,value='1.25'):
    attrs={'host_subject_id':'PRIVATE-SYNTHETIC-ID','status':phase,'supplement':'potato','semester':'fall15','collection_date':'2015-11-01','acetate':value,'butyrate':'NaN','propionate':'missing','total SCFA':'Inf'}
    inner=''.join(f'<SAMPLE_ATTRIBUTE><TAG>{k}</TAG><VALUE>{v}</VALUE></SAMPLE_ATTRIBUTE>' for k,v in attrs.items())
    return f'<SAMPLE accession="{acc}"><SAMPLE_ATTRIBUTES>{inner}</SAMPLE_ATTRIBUTES></SAMPLE>'


def test_aggregate_only_and_numeric_flags():
    xml='<SAMPLE_SET>'+sample('A','before')+sample('B','during')+'</SAMPLE_SET>'
    result=load().summarize(io.BytesIO(xml.encode()),2)
    assert result['subject_keys']==1
    assert result['subjects_with_both_phases_ge1']==1
    assert result['subjects_with_both_phases_ge3']==0
    assert result['outcome_numeric_parseable_counts']=={'acetate':2}
    rendered=json.dumps(result)
    assert 'PRIVATE-SYNTHETIC-ID' not in rendered and '1.25' not in rendered
    assert result['outcomes_retained'] is False


def test_project_record_is_not_empty_cohort():
    with pytest.raises(AssertionError,match='Unreconciled'):
        load().summarize(io.BytesIO(b'<PROJECT_SET><PROJECT/></PROJECT_SET>'),1201)


def test_duplicate_accessions_fail_reconciliation():
    xml='<SAMPLE_SET>'+sample('A','before')+sample('A','during')+'</SAMPLE_SET>'
    with pytest.raises(AssertionError):
        load().summarize(io.BytesIO(xml.encode()),2)


def test_recorded_result_and_scope():
    r=json.loads(Path('results/resistant_starch_metadata_census_corrected_20261007.json').read_text())
    assert r['sample_count']==r['unique_sample_accessions']==1201
    assert r['subject_keys']==175 and r['subjects_with_both_phases_ge3']==143
    assert sum(r['phase_counts'].values())==1201
    assert r['independent_validation'] is False and r['outcomes_retained'] is False
    assert r['byte_count']<20*1024*1024 and r['seconds']<60
