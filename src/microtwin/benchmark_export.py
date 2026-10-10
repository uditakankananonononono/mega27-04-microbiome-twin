"""Bounded loss-report orchestration with explicit subject/fold checks.

Imports submitted errors, not models. Does not authenticate provenance or losses.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
import pandas as pd
from .interaction_score import heldout_scores
from .reliability import reliability_report
from .research_intake import _read_rectangular_text


def export_paired_report(loss_file, partition_file, *, n_boot=2000, seed=0):
    if type(n_boot) is not int or not 0<=n_boot<=10000:
        raise ValueError('n_boot must be an integer from 0 to 10000')
    if type(seed) is not int or seed<0:
        raise ValueError('seed must be a nonnegative integer')
    paths=[Path(loss_file),Path(partition_file)]
    if any(not p.is_file() or p.stat().st_size>10_000_000 for p in paths):
        raise ValueError('two existing CSV files required, at most 10 MB each')
    raw=[p.read_bytes() for p in paths]
    losses=_read_rectangular_text(paths[0],delimiter=',',label='loss CSV')
    parts=_read_rectangular_text(paths[1],delimiter=',',label='partition CSV')
    if set(losses.columns)!={'sample_id','subject_id','fold','prior_error','interaction_error'}:
        raise ValueError('loss CSV requires sample_id,subject_id,fold,prior_error,interaction_error')
    if set(parts.columns)!={'sample_id','subject_id','fold','partition'}:
        raise ValueError('partition CSV requires sample_id,subject_id,fold,partition')
    if losses.empty or parts.empty:raise ValueError('nonempty loss/partition CSV required')
    for df in [losses,parts]:
        for col in ['sample_id','subject_id','fold']:
            if not df[col].map(lambda v:isinstance(v,str) and bool(v) and v==v.strip()).all():
                raise ValueError('nonempty IDs without surrounding whitespace required')
    if losses.sample_id.duplicated().any():raise ValueError('each sample must have exactly one outer-test loss')
    if parts.duplicated(['sample_id','fold']).any():raise ValueError('duplicate sample in fold manifest')
    if not set(parts.partition)<= {'train','validation','test'}:raise ValueError('invalid partition')
    if parts.groupby('sample_id').subject_id.nunique().gt(1).any():raise ValueError('sample maps to inconsistent subjects')
    if set(losses.fold)!=set(parts.fold):raise ValueError('loss/manifest folds must match')
    for fold,p in parts.groupby('fold'):
        if not {'train','test'}<=set(p.partition):raise ValueError('each fold needs train and test')
        if p.groupby('subject_id').partition.nunique().gt(1).any():
            raise ValueError('subject crosses partitions within fold')
    test=parts[parts.partition=='test']
    if test.sample_id.duplicated().any():raise ValueError('sample appears in multiple outer-test folds')
    a=set(map(tuple,losses[['sample_id','subject_id','fold']].to_numpy()))
    b=set(map(tuple,test[['sample_id','subject_id','fold']].to_numpy()))
    if a!=b:raise ValueError('losses must exactly match outer-test manifest')
    try:
        for field in ('prior_error','interaction_error'):
            losses[field]=pd.to_numeric(losses[field],errors='raise')
    except (ValueError,TypeError) as exc:
        raise ValueError('numeric loss entries required') from exc
    score=heldout_scores(losses.prior_error.to_numpy(),losses.interaction_error.to_numpy(),
                         ids=losses.sample_id.tolist(),groups=losses.subject_id.tolist(),n_boot=n_boot,seed=seed)
    components={}
    if score['ecosystem_score'] is not None:
        components['interaction_dependence']={'value':score['ecosystem_score'],'source':'submitted paired outer-test losses'}
    if any(p.read_bytes()!=r for p,r in zip(paths,raw)):raise ValueError('inputs changed during report')
    return {'status':'submitted_loss_report_not_a_model_run','n_samples':len(losses),
            'n_subject_labels':losses.subject_id.nunique(),'n_folds':losses.fold.nunique(),
            'subject_partition_check':'exact_submitted_labels_passed','source_independence_verified':False,
            'external_win_certified':False,'input_sha256':[hashlib.sha256(r).hexdigest() for r in raw],
            'predictive_dependence':score,'reliability':reliability_report(components),
            'limitations':['Submitted errors and subject labels are not independently verified.',
                           'No model fitting, assay audit, source-family certification or clinical prediction.',
                           'Other reliability components stay missing; no composite index is invented.']}
