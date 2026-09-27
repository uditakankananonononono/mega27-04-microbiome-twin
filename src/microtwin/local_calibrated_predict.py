"""Research-only local composition predictions with split-calibrated error radius.

Training and calibration must be labeled, disjoint, same-assay files. A caller
assertion of source/assay match is not an external rights or exchangeability
proof. The radius is marginal under exchangeability, not personalized.
"""
from __future__ import annotations

import hashlib
import csv
from pathlib import Path

import numpy as np

from .conformal import bray_radius
from .data import bray_curtis
from .local_predict import _read_table, predict_local
from .research_intake import inspect_local_matrix


def predict_with_radius(train_path, calibration_path, query_path, *, unit, source_id,
                        processing_authorized=False, subject_map=None, calibration_subject_map=None,
                        query_subject_map=None, alpha=.1):
    maps=(subject_map,calibration_subject_map,query_subject_map)
    if any(path is not None for path in maps) and not all(path is not None for path in maps):
        raise ValueError('train, calibration and query subject maps must be supplied together')
    if all(path is not None for path in maps):
        all_paths=[Path(p).resolve() for p in (train_path,calibration_path,query_path,*maps)]
        if len(set(all_paths))!=len(all_paths):
            raise ValueError('input tables and subject map paths must all be distinct')
    if len({Path(train_path).resolve(), Path(calibration_path).resolve(), Path(query_path).resolve()}) != 3:
        raise ValueError('training, calibration and query paths must be distinct')
    pred, report = predict_local(train_path, query_path, unit=unit, source_id=source_id,
                                 processing_authorized=processing_authorized, subject_map=subject_map)
    qc = inspect_local_matrix(calibration_path, unit=unit, source_id=source_id,
                              processing_authorized=processing_authorized)
    train_ids, taxa, _, train_hash = _read_table(train_path)
    cal_ids, cal_taxa, xcal, cal_hash = _read_table(calibration_path)
    query_ids, query_taxa, _, query_hash = _read_table(query_path)
    if len(set(train_ids) & set(cal_ids)) or len(set(query_ids) & set(cal_ids)):
        raise ValueError('training, calibration and query sample IDs must be disjoint')
    subject_hashes=[]
    if all(path is not None for path in maps):
        subject_sets=[]
        for path, ids in zip(maps,(train_ids,cal_ids,query_ids)):
            file=Path(path)
            if not file.is_file() or file.stat().st_size>50_000_000:
                raise ValueError('missing or oversized subject map')
            data=file.read_bytes(); subject_hashes.append(hashlib.sha256(data).hexdigest())
            with file.open(newline='') as handle:
                rows=list(csv.reader(handle))
            if not rows or rows[0]!=['sample_id','subject_id'] or len(rows)!=len(ids)+1 or any(len(row)!=2 for row in rows[1:]):
                raise ValueError('subject map needs exactly sample_id,subject_id and one row per sample')
            sample=[r[0] for r in rows[1:]]; subjects=[r[1] for r in rows[1:]]
            if len(set(sample))!=len(sample) or set(sample)!=set(ids) or any(not v.strip() for v in subjects):
                raise ValueError('subject map must exactly cover partition sample IDs with nonempty subjects')
            subject_sets.append(set(subjects))
        if any(subject_sets[i]&subject_sets[j] for i,j in ((0,1),(0,2),(1,2))):
            raise ValueError('subject ID crosses training, calibration and query partitions')
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
    for path, expected in zip(maps,subject_hashes):
        try:
            current=hashlib.sha256(Path(path).read_bytes()).hexdigest()
        except OSError as e:
            raise ValueError('subject map changed during calibrated prediction') from e
        if current!=expected:
            raise ValueError('subject map changed during calibrated prediction')
    report['subject_partition_check']={'status':'exact_submitted_labels_disjoint' if subject_hashes else 'unverified_no_maps',
                                       'subject_map_sha256':dict(zip(('train','calibration','query'),subject_hashes)),
                                       'limitation':'Exact supplied pseudonyms cannot prove distinct people or cross-source exchangeability.'}
    report['calibration_sha256']=cal_hash
    report['calibration_samples']=len(cal_ids)
    report['uncertainty']={'metric':'Bray-Curtis error radius','radius':bound['radius'],
                           'alpha':bound['alpha'],'quantile_rank':bound['quantile_rank'],
                           'vacuous':bound['vacuous'],
                           'scope':'finite_sample_marginal_only_if_calibration_and_query_exchangeable',
                           'same_source_and_assay_proof':False,
                           'subject_separation_proof':'exact_submitted_labels_only' if subject_hashes else 'unverified',
                           'note':'User-supplied source_id/name equality does not certify assay, subject independence or exchangeability. No conditional, cross-source or clinical coverage claim.'}
    return pred, report
