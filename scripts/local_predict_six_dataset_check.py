"""Real-data numerical check of the local CLI baseline on six cNODE tables.

Internal same-dataset folds only. This cannot establish external transfer,
clinical utility or a top-tool win. No result is used to tune the predictor.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from microtwin.data import DATASETS, load, bray_curtis
from microtwin.evaluate import kfold_indices
from microtwin.models import PresenceMean


def score_dataset(name, *, k=10):
    if name not in DATASETS:raise ValueError('unknown cNODE dataset')
    z,p=load(name)
    err=np.full(len(z),np.nan)
    for fold in kfold_indices(len(z),min(k,len(z)),seed=0):
        train=np.setdiff1d(np.arange(len(z)),fold)
        pred=PresenceMean().fit(z[train],p[train]).predict(z[fold])
        err[fold]=bray_curtis(pred,p[fold])
    if not np.isfinite(err).all():raise ValueError('incomplete folds')
    src=ROOT/'data/raw/cnode'/f'{name}.csv'
    return {'dataset':name,'samples_after_assemblage_dedup':len(z),'taxa':z.shape[1],
            'folds':min(k,len(z)),'median_bray_curtis':float(np.median(err)),
            'mean_bray_curtis':float(np.mean(err)),
            'data_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
            'scope':'internal_same_dataset_cross_validation_not_external_source_transfer'}


if __name__=='__main__':
    result={'model':'presence_mean_identical_to_local_predict_formula',
            'seed':0,'all_datasets':[score_dataset(name) for name in DATASETS],
            'note':'Same six viewed cNODE tables and same-dataset 10-fold CV. No external study or source-family held out. No model selection, interaction necessity, intervention or clinical claim.'}
    path=ROOT/'results/local_predict_six_dataset_check.json'
    path.write_text(json.dumps(result,indent=2)+'\n')
    print(path)
    for r in result['all_datasets']:
        print(r['dataset'],r['samples_after_assemblage_dedup'],round(r['median_bray_curtis'],6))
