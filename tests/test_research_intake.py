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
