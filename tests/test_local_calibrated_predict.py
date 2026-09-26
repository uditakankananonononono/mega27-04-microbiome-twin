import json

import numpy as np
import pandas as pd
import pytest

from microtwin.cli import main
from microtwin.local_calibrated_predict import predict_with_radius


def _inputs(tmp_path, n=20):
    tr=tmp_path/'train.tsv'; tr.write_text('sample_id\tA\tB\ns1\t8\t2\ns2\t4\t6\n')
    cal=tmp_path/'cal.tsv';cal.write_text('sample_id\tA\tB\n'+''.join(f'c{i}\t3\t7\n' for i in range(n)))
    q=tmp_path/'query.tsv';q.write_text('sample_id\tA\tB\nq1\t1\t1\n')
    return tr,cal,q


def test_local_calibration_radius_and_provenance(tmp_path):
    tr,cal,q=_inputs(tmp_path)
    pred, r=predict_with_radius(tr,cal,q,unit='counts',source_id='test',processing_authorized=True)
    np.testing.assert_allclose(pred[['A','B']].to_numpy(),[[.6,.4]])
    assert r['calibration_samples']==20 and len(r['calibration_sha256'])==64
    assert r['uncertainty']['vacuous'] is False
    assert np.isclose(r['uncertainty']['radius'], .3)
    assert r['uncertainty']['same_source_and_assay_proof'] is False
    assert r['external_validation'] is False


def test_too_little_calibration_is_vacuous(tmp_path):
    tr,cal,q=_inputs(tmp_path,n=2)
    _,r=predict_with_radius(tr,cal,q,unit='counts',source_id='test',processing_authorized=True)
    assert r['uncertainty']['radius']==1 and r['uncertainty']['vacuous']


def test_calibration_rejects_overlap_and_unseen_taxon(tmp_path):
    tr,cal,q=_inputs(tmp_path)
    cal.write_text('sample_id\tA\tB\ns1\t3\t7\n')
    with pytest.raises(ValueError,match='disjoint'):
        predict_with_radius(tr,cal,q,unit='counts',source_id='test',processing_authorized=True)
    tr.write_text('sample_id\tA\tB\ns1\t8\t0\ns2\t4\t0\n')
    cal.write_text('sample_id\tA\tB\nc1\t3\t7\n')
    q.write_text('sample_id\tA\tB\nq1\t1\t0\n')
    with pytest.raises(ValueError,match='absent in training'):
        predict_with_radius(tr,cal,q,unit='counts',source_id='test',processing_authorized=True)


def test_calibrated_cli_writes_once(tmp_path, capsys):
    tr,cal,q=_inputs(tmp_path)
    out=tmp_path/'result.csv'
    argv=['predict-calibrated',str(tr),str(cal),str(q),'--unit','counts',
          '--source-id','test','--processing-authorized','--out',str(out)]
    assert main(argv)==0
    report=json.loads(capsys.readouterr().out)
    assert report['output_file']==str(out)
    assert report['uncertainty']['radius']==pytest.approx(.3)
    assert pd.read_csv(out)['sample_id'].tolist()==['q1']
    with pytest.raises(SystemExit,match='already exists'):
        main(argv)
