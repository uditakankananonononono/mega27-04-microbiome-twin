import pytest
from microtwin.subject_partition import check_two_maps
from microtwin.local_calibrated_predict import predict_with_radius


@pytest.mark.parametrize('payload', [b'sample_id,subject_id\nq1,"PRIVATE_SUBJECT',
    b'sample_id,subject_id\nq1,"PRIVATE"junk\n',
    b'sample_id,subject_id\nq1,\xffPRIVATE\n'])
def test_partition_guards_reject_malformed_quotes_and_decode_without_private_details(tmp_path, payload):
    tr=tmp_path/'tr.csv';tr.write_text('sample_id,subject_id\nt1,p1\n')
    ca=tmp_path/'ca.csv';ca.write_text('sample_id,subject_id\nc1,p2\n')
    qu=tmp_path/'qu.csv';qu.write_bytes(payload)
    with pytest.raises(ValueError) as error:
        check_two_maps(tr,qu,['t1'],['q1'])
    assert str(error.value)=='subject map must contain valid UTF-8 and well-formed CSV records'
    assert 'PRIVATE' not in str(error.value)
    train=tmp_path/'train.tsv';train.write_text('sample_id\tA\nt1\t2\n')
    cal=tmp_path/'cal.tsv';cal.write_text('sample_id\tA\nc1\t2\n')
    query=tmp_path/'query.tsv';query.write_text('sample_id\tA\nq1\t1\n')
    with pytest.raises(ValueError,match='valid UTF-8 and well-formed CSV'):
        predict_with_radius(train,cal,query,unit='counts',source_id='demo',processing_authorized=True,
                            subject_map=tr,calibration_subject_map=ca,query_subject_map=qu)


def test_strict_guard_preserves_valid_quoted_subjects(tmp_path):
    tr=tmp_path/'tr.csv';tr.write_text('sample_id,subject_id\nt1,"person, one"\n')
    qu=tmp_path/'qu.csv';qu.write_text('sample_id,subject_id\nq1,"person, two"\n')
    assert len(check_two_maps(tr,qu,['t1'],['q1']))==2
    qu.write_text('sample_id,subject_id\nq1,"person, one"\n')
    with pytest.raises(ValueError,match='crosses'):
        check_two_maps(tr,qu,['t1'],['q1'])
