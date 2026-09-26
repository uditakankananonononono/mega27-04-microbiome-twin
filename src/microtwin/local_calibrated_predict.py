"""Research-only local composition predictions with split-calibrated error radius.

Training and calibration must be labeled, disjoint, same-assay files. A caller
assertion of source/assay match is not an external rights or exchangeability
proof. The radius is marginal under exchangeability, not personalized.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np

from .conformal import bray_radius
from .data import bray_curtis
from .local_predict import _read_table, predict_local
from .research_intake import inspect_local_matrix


def predict_with_radius(train_path, calibration_path, query_path, *, unit, source_id,
                        processing_authorized=False, subject_map=None, alpha=.1):
    pred, report = predict_local(train_path, query_path, unit=unit, source_id=source_id,
                                 processing_authorized=processing_authorized, subject_map=subject_map)
    qc = inspect_local_matrix(calibration_path, unit=unit, source_id=source_id,
                              processing_authorized=processing_authorized)
    train_ids, taxa, _, train_hash = _read_table(train_path)
    cal_ids, cal_taxa, xcal, cal_hash = _read_table(calibration_path)
    query_ids, query_taxa, _, query_hash = _read_table(query_path)
    if len(set(train_ids) & set(cal_ids)) or len(set(query_ids) & set(cal_ids)):
        raise ValueError('training, calibration and query sample IDs must be disjoint')
    if cal_taxa != taxa or query_taxa != taxa:
        raise ValueError('calibration and query taxa/order must match training exactly')
    if cal_hash != qc['sha256'] or train_hash != report['train_sha256'] or query_hash != report['query_sha256']:
        raise ValueError('input changed during calibrated prediction')
    if unit == 'counts' and (xcal != np.floor(xcal)).any():
        raise ValueError('calibration counts must be integers')
    if unit == 'relative_abundance' and not np.allclose(xcal.sum(axis=1),1,atol=1e-4,rtol=1e-4):
        raise ValueError('calibration relative abundances must sum to one')
    # Frozen PresenceMean formula, same as predict_local, with a separate
    # calibration assemblage derived from labeled calibration rows.
    _, _, xtr, duplicate_hash = _read_table(train_path)
    if duplicate_hash != train_hash:
        raise ValueError('training file changed during calibration')
    train_mean=(xtr/xtr.sum(axis=1,keepdims=True)).mean(axis=0)
    zcal=(xcal>0).astype(float)
    if (zcal[:,train_mean<=0]>0).any():
        raise ValueError('calibration contains taxa absent in training; abstaining')
    mass=zcal@(train_mean+1e-9)
    cal_pred=zcal*(train_mean+1e-9)/mass[:,None]
    truth=xcal/xcal.sum(axis=1,keepdims=True)
    errors=bray_curtis(cal_pred,truth)
    bound=bray_radius(errors,alpha)
    # Final checks before the caller writes output. A same-path replacement is
    # detected before publishing rather than silently switching evidence.
    for path, expected in [(train_path,train_hash),(calibration_path,cal_hash),(query_path,query_hash)]:
        if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=expected:
            raise ValueError('input changed during calibrated prediction')
    report['calibration_sha256']=cal_hash
    report['calibration_samples']=len(cal_ids)
    report['uncertainty']={'metric':'Bray-Curtis error radius','radius':bound['radius'],
                           'alpha':bound['alpha'],'quantile_rank':bound['quantile_rank'],
                           'vacuous':bound['vacuous'],
                           'scope':'finite_sample_marginal_only_if_calibration_and_query_exchangeable',
                           'same_source_and_assay_proof':False,
                           'note':'User-supplied source_id/name equality does not certify assay, subject independence or exchangeability. No conditional, cross-source or clinical coverage claim.'}
    return pred, report
