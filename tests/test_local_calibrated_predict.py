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


def test_same_file_paths_rejected_even_before_fit(tmp_path):
    tr,cal,q=_inputs(tmp_path)
    with pytest.raises(ValueError,match='paths must be distinct'):
        predict_with_radius(tr,tr,q,unit='counts',source_id='test',processing_authorized=True)


def test_calibrated_input_hash_change_is_detected(tmp_path, monkeypatch):
    from microtwin import local_calibrated_predict as module
    tr,cal,q=_inputs(tmp_path)
    original=module.bray_radius
    def tamper_then_radius(errors,alpha):
        q.write_text('sample_id\tA\tB\nq1\t0\t1\n')
        return original(errors,alpha)
    monkeypatch.setattr(module,'bray_radius',tamper_then_radius)
    with pytest.raises(ValueError,match='input changed'):
        predict_with_radius(tr,cal,q,unit='counts',source_id='test',processing_authorized=True)


def _maps(tmp_path, overlap=False):
    files=[tmp_path/'train-map.csv',tmp_path/'cal-map.csv',tmp_path/'query-map.csv']
    files[0].write_text('sample_id,subject_id\ns1,p1\ns2,p1\n')
    files[1].write_text('sample_id,subject_id\n'+''.join(f'c{i},p2\n' for i in range(20)))
    files[2].write_text('sample_id,subject_id\nq1,'+('p2' if overlap else 'p3')+'\n')
    return files


def test_calibrated_subject_guard_pass_and_overlap(tmp_path):
    tr,cal,q=_inputs(tmp_path)
    maps=_maps(tmp_path)
    kwargs=dict(unit='counts',source_id='test',processing_authorized=True,
                subject_map=maps[0],calibration_subject_map=maps[1],query_subject_map=maps[2])
    _,report=predict_with_radius(tr,cal,q,**kwargs)
    assert report['subject_partition_check']['status']=='exact_submitted_labels_disjoint'
    assert len(report['subject_partition_check']['subject_map_sha256'])==3
    _maps(tmp_path,overlap=True)
    with pytest.raises(ValueError,match='crosses'):
        predict_with_radius(tr,cal,q,**kwargs)
    with pytest.raises(ValueError,match='supplied together'):
        predict_with_radius(tr,cal,q,unit='counts',source_id='test',processing_authorized=True,subject_map=maps[0])


def test_subject_map_missing_extra_and_mutation(tmp_path, monkeypatch):
    from microtwin import local_calibrated_predict as module
    tr,cal,q=_inputs(tmp_path)
    maps=_maps(tmp_path)
    kwargs=dict(unit='counts',source_id='test',processing_authorized=True,
                subject_map=maps[0],calibration_subject_map=maps[1],query_subject_map=maps[2])
    maps[2].write_text('sample_id,subject_id\nwrong,p3\n')
    with pytest.raises(ValueError,match='exactly cover'):
        predict_with_radius(tr,cal,q,**kwargs)
    _maps(tmp_path)
    original=module.bray_radius
    def mutate(errors,alpha):
        maps[2].write_text('sample_id,subject_id\nq1,p4\n')
        return original(errors,alpha)
    monkeypatch.setattr(module,'bray_radius',mutate)
    with pytest.raises(ValueError,match='subject map changed'):
        predict_with_radius(tr,cal,q,**kwargs)


def test_subject_map_whitespace_cannot_hide_cross_partition_person(tmp_path):
    tr,cal,q=_inputs(tmp_path)
    maps=_maps(tmp_path)
    args=dict(unit='counts',source_id='test',processing_authorized=True,
              subject_map=maps[0],calibration_subject_map=maps[1],query_subject_map=maps[2])
    maps[2].write_text('sample_id,subject_id\nq1, p1 \n')
    with pytest.raises(ValueError,match='surrounding whitespace'):
        predict_with_radius(tr,cal,q,**args)
    maps[2].write_text('sample_id,subject_id\n q1,p3\n')
    with pytest.raises(ValueError,match='surrounding whitespace'):
        predict_with_radius(tr,cal,q,**args)
    maps[2].write_text('sample_id,subject_id\nq1,"p,3"\n')
    _,report=predict_with_radius(tr,cal,q,**args)
    assert report['subject_partition_check']['status']=='exact_submitted_labels_disjoint'
