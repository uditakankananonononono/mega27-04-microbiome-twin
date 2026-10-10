import json

import pytest

from microtwin.cli import main
from microtwin.research_intake import inspect_local_matrix


def test_local_intake_requires_declaration_and_maps_exact_subjects(tmp_path, capsys):
    matrix = tmp_path/'counts.tsv'
    matrix.write_text('sample_id\tA\tB\ns1\t2\t0\ns2\t0\t1\n')
    mapping = tmp_path/'groups.csv'
    mapping.write_text('sample_id,subject_id\ns1,p1\ns2,p1\n')
    with pytest.raises(ValueError,match='authorization'):
        inspect_local_matrix(matrix,unit='counts',source_id='demo')
    result = inspect_local_matrix(matrix,unit='counts',source_id='demo',processing_authorized=True,subject_map=mapping)
    assert result['subject_groups']==1 and result['grouped_split_ready'] is False
    assert 'subject_map_sha256' not in result
    assert 's1' not in json.dumps(result) and 'p1' not in json.dumps(result)
    assert result['prediction'] is None and not result['external_validation']
    assert main(['inspect',str(matrix),'--unit','counts','--source-id','demo','--processing-authorized','--subject-map',str(mapping)])==0
    cli_result=json.loads(capsys.readouterr().out)
    assert cli_result['status']=='schema_validated_only'
    assert 'subject_map_sha256' not in cli_result


def test_local_intake_fails_on_bad_columns_missing_data_and_fractional_counts(tmp_path):
    p=tmp_path/'x.tsv'
    for text in ('sample_id\tA\tB\ns1\t1\t\n', 'sample_id\tA\tB\ns1\t1.2\t0\n',
                 'sample_id\tA\tB\ns1\t1\tbad\n', 'sample_id\tA\tA\ns1\t1\t0\n'):
        p.write_text(text)
        with pytest.raises(ValueError):
            inspect_local_matrix(p,unit='counts',source_id='demo',processing_authorized=True)


def test_subject_map_extras_and_missing_rejected(tmp_path):
    p=tmp_path/'x.tsv';p.write_text('sample_id\tA\ns1\t1\ns2\t2\n')
    m=tmp_path/'g.csv';m.write_text('sample_id,subject_id\ns1,p1\ns3,p2\n')
    with pytest.raises(ValueError,match='subject map'):
        inspect_local_matrix(p,unit='counts',source_id='demo',processing_authorized=True,subject_map=m)


@pytest.mark.parametrize('text', [
    'sample_id\tA\ns1\t1\t99\ns2\t2\t88\n',
    'sample_id\tA\tB\ns1\t1\n',
    'sample_id\tA\ns1\t1\ns2\t2\tSECRET_LABEL\t3\n',
    'sample_id\tA\n"SECRET_UNCLOSED\t1\n',
])
def test_ragged_or_malformed_matrix_fails_without_parser_details(tmp_path, text):
    p=tmp_path/'private_path.tsv';p.write_text(text)
    with pytest.raises(ValueError) as error:
        inspect_local_matrix(p,unit='counts',source_id='demo',processing_authorized=True)
    assert str(error.value)=='input must be a readable rectangular text table with unique headers'
    assert 'SECRET' not in str(error.value) and str(p) not in str(error.value)


@pytest.mark.parametrize('text', [
    'sample_id,subject_id\ns1,p1,extra\ns2,p2,extra\n',
    'sample_id,subject_id\ns1\ns2,p2\n',
    'sample_id,subject_id\ns1,"SECRET_UNCLOSED\n',
])
def test_ragged_subject_map_rejected_before_index_inference(tmp_path, text):
    p=tmp_path/'x.tsv';p.write_text('sample_id\tA\ns1\t1\ns2\t2\n')
    m=tmp_path/'g.csv';m.write_text(text)
    with pytest.raises(ValueError,match='subject map must be a readable rectangular'):
        inspect_local_matrix(p,unit='counts',source_id='demo',processing_authorized=True,subject_map=m)


def test_rectangular_intake_preserves_quoted_delimiters(tmp_path):
    p=tmp_path/'x.csv';p.write_text('sample_id,"Taxon, A"\n"sample, one",1\n"sample, two",2\n')
    result=inspect_local_matrix(p,unit='counts',source_id='demo',processing_authorized=True)
    assert result['samples']==2 and result['taxa']==1
