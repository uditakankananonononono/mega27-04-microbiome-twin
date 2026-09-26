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
    np.testing.assert_allclose(pred[['A','B','C']].to_numpy(),[[.6,.4,0],[0,1,0]])
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
