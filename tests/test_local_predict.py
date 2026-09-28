import json

import numpy as np
import pandas as pd
import pytest

from microtwin.cli import main
from microtwin.local_predict import predict_local


def test_local_population_prediction_and_cli(tmp_path, capsys):
    train = tmp_path/'train.tsv'; train.write_text('sample_id\tA\tB\tC\ns1\t8\t2\t0\ns2\t4\t6\t0\n')
    query = tmp_path/'query.tsv'; query.write_text('sample_id\tA\tB\tC\nq1\t1\t1\t0\nq2\t0\t1\t0\n')
    out = tmp_path/'pred.csv'
    assert main(['predict',str(train),str(query),'--unit','counts','--source-id','test',
                 '--processing-authorized','--out',str(out)]) == 0
    pred = pd.read_csv(out)
    assert pred.sample_id.tolist()==['q1','q2']
    np.testing.assert_allclose(pred[['A','B','C']].to_numpy(),[[.6,.4,0],[0,1,0]],atol=1e-8)
    report=json.loads(capsys.readouterr().out)
    assert report['uncertainty'] is None and report['external_validation'] is False
    assert report['query_min_known_taxon_fraction']==1


def test_predict_abstains_bad_queries(tmp_path):
    train=tmp_path/'train.tsv';train.write_text('sample_id\tA\tB\ns1\t2\t0\ns2\t1\t0\n')
    q=tmp_path/'query.tsv'
    base={'unit':'counts','source_id':'test','processing_authorized':True}
    for text, reason in [('sample_id\tA\tB\ns1\t1\t0\n','overlaps'),
                         ('sample_id\tB\tA\nq1\t1\t0\n','order'),
                         ('sample_id\tA\tB\nq1\t2\t0\n','binary'),
                         ('sample_id\tA\tB\nq1\t0\t1\n','abstaining')]:
        q.write_text(text)
        with pytest.raises(ValueError,match=reason):predict_local(train,q,**base)
    with pytest.raises(ValueError,match='authorization'):predict_local(train,q,unit='counts',source_id='test')


def test_predict_cli_refuses_existing_output(tmp_path, capsys):
    train=tmp_path/'train.tsv';train.write_text('sample_id\tA\tB\ns1\t2\t1\n')
    query=tmp_path/'query.tsv';query.write_text('sample_id\tA\tB\nq1\t1\t0\n')
    out=tmp_path/'existing.csv';out.write_text('DO NOT CHANGE')
    with pytest.raises(SystemExit,match='already exists'):
        main(['predict',str(train),str(query),'--unit','counts','--source-id','test',
              '--processing-authorized','--out',str(out)])
    assert out.read_text()=='DO NOT CHANGE'


def test_predict_detects_query_mutation_between_read_and_hash(tmp_path, monkeypatch):
    from microtwin import local_predict
    train=tmp_path/'train.tsv';train.write_text('sample_id\tA\tB\ns1\t2\t1\n')
    query=tmp_path/'query.tsv';query.write_text('sample_id\tA\tB\nq1\t1\t0\n')
    original=local_predict._read_table
    def mutate_after_query_read(path):
        result=original(path)
        if str(path)==str(query):query.write_text('sample_id\tA\tB\nq1\t0\t1\n')
        return result
    monkeypatch.setattr(local_predict,'_read_table',mutate_after_query_read)
    with pytest.raises(ValueError,match='query file changed'):
        local_predict.predict_local(train,query,unit='counts',source_id='test',processing_authorized=True)


def test_predict_detects_training_mutation_between_inspection_and_read(tmp_path, monkeypatch):
    from microtwin import local_predict
    train=tmp_path/'train.tsv';train.write_text('sample_id\tA\tB\ns1\t2\t1\n')
    query=tmp_path/'query.tsv';query.write_text('sample_id\tA\tB\nq1\t1\t0\n')
    original=local_predict.inspect_local_matrix
    def mutate_after_inspection(*args,**kwargs):
        result=original(*args,**kwargs)
        train.write_text('sample_id\tA\tB\ns1\t1\t2\n')
        return result
    monkeypatch.setattr(local_predict,'inspect_local_matrix',mutate_after_inspection)
    with pytest.raises(ValueError,match='training file changed'):
        local_predict.predict_local(train,query,unit='counts',source_id='test',processing_authorized=True)


def test_predict_detects_subject_map_mutation(tmp_path, monkeypatch):
    from microtwin import local_predict
    train=tmp_path/'train.tsv';train.write_text('sample_id\tA\tB\ns1\t2\t1\ns2\t1\t2\n')
    query=tmp_path/'query.tsv';query.write_text('sample_id\tA\tB\nq1\t1\t0\n')
    mapping=tmp_path/'groups.csv';mapping.write_text('sample_id,subject_id\ns1,p1\ns2,p2\n')
    original=local_predict._read_table
    def mutate_after_query_read(path):
        result=original(path)
        if str(path)==str(query):mapping.write_text('sample_id,subject_id\ns1,p1\ns2,p1\n')
        return result
    monkeypatch.setattr(local_predict,'_read_table',mutate_after_query_read)
    with pytest.raises(ValueError,match='subject map changed'):
        local_predict.predict_local(train,query,unit='counts',source_id='test',processing_authorized=True,subject_map=mapping)


def test_local_predict_matches_archived_presence_mean_exactly(tmp_path):
    from microtwin.models import PresenceMean
    train=tmp_path/'train.tsv';train.write_text('sample_id\tA\tB\tC\ns1\t5\t2\t0\ns2\t0\t1\t9\n')
    query=tmp_path/'query.tsv';query.write_text('sample_id\tA\tB\tC\nq1\t1\t1\t0\nq2\t1\t0\t1\n')
    pred,_=predict_local(train,query,unit='counts',source_id='test',processing_authorized=True)
    x=np.array([[5.,2.,0.],[0.,1.,9.]])
    expected=PresenceMean().fit((x>0).astype(float),x/x.sum(1,keepdims=True)).predict(
        np.array([[1.,1.,0.],[1.,0.,1.]]))
    np.testing.assert_array_equal(pred[['A','B','C']].to_numpy(),expected)


def test_predict_cli_requires_csv_output(tmp_path):
    train=tmp_path/'train.tsv';train.write_text('sample_id\tA\ns1\t2\n')
    query=tmp_path/'query.tsv';query.write_text('sample_id\tA\nq1\t1\n')
    with pytest.raises(SystemExit,match='end in .csv'):
        main(['predict',str(train),str(query),'--unit','counts','--source-id','test',
              '--processing-authorized','--out',str(tmp_path/'wrong.tsv')])


def test_predict_detects_subject_map_change_during_inspection(tmp_path, monkeypatch):
    from microtwin import local_predict
    train=tmp_path/"train.tsv";train.write_text("sample_id\tA\ntr1\t2\n")
    query=tmp_path/"query.tsv";query.write_text("sample_id\tA\nq1\t1\n")
    mapping=tmp_path/"groups.csv";mapping.write_text("sample_id,subject_id\ntr1,p1\n")
    original=local_predict.inspect_local_matrix
    def mutate_after(*args,**kwargs):
        result=original(*args,**kwargs)
        mapping.write_text("sample_id,subject_id\ntr1,p2\n")
        return result
    monkeypatch.setattr(local_predict,"inspect_local_matrix",mutate_after)
    with pytest.raises(ValueError,match="subject map changed during inspection"):
        local_predict.predict_local(train,query,unit="counts",source_id="test",
                                    processing_authorized=True,subject_map=mapping)
