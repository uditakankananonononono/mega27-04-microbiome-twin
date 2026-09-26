"""Independent arithmetic readback of the viewed EMP development metric.

This is not a second source, model or benchmark. It reconstructs the prior
without importing the project model/evaluator, on the same filtered data.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/source_family_candidates/EMP'
TABLE=BASE/'emp_2k_unambiguous_genus.tsv.gz'
META=BASE/'emp_mapping_subset_2k.tsv'
INFO=BASE/'emp_2k_unambiguous_genus_info.json'
REPORTED=ROOT/'results/emp_leave_study_development.json'


def check():
    info=json.loads(INFO.read_text()); reported=json.loads(REPORTED.read_text())
    if hashlib.sha256(TABLE.read_bytes()).hexdigest()!=info['output_sha256'] or reported['table_sha256']!=info['output_sha256']:
        raise ValueError('EMP table hash mismatch')
    meta_sha=hashlib.sha256(META.read_bytes()).hexdigest()
    if meta_sha!='0e4a9d960ec7ccebc0dd4d7de9e4e4ab98abe52aad7f117ea3746d6ab2dd0d39' or meta_sha!=reported['metadata_sha256']:
        raise ValueError('EMP metadata hash mismatch')
    values=pd.read_csv(TABLE,sep='\t',index_col=0)
    metadata=pd.read_csv(META,sep='\t',low_memory=False).set_index('#SampleID').loc[values.columns]
    rows=[]
    for record in reported['study_results']:
        if record['status']!='viewed_leave_study_out_development_only':continue
        study=record['study_id']
        sample_names=metadata.index[metadata.study_id==study]
        others=values.drop(columns=sample_names).to_numpy(float).T
        held=values[sample_names].to_numpy(float).T
        known=others.sum(0)>0
        retained=held[:,known].sum(1)/held.sum(1)
        eligible=retained>=reported['threshold_on_retained_genus_subset']
        if eligible.sum()!=record['covered_samples']:
            raise ValueError('different eligible rows')
        normalized=others/others.sum(1,keepdims=True)
        mean_weight=normalized.mean(0)+1e-9
        present=(held[eligible]>0)
        pred=present*mean_weight
        pred/=pred.sum(1,keepdims=True)
        truth=held[eligible]/held[eligible].sum(1,keepdims=True)
        err=np.abs(pred-truth).sum(1)/np.maximum((pred+truth).sum(1),1e-12)
        labels=metadata.loc[sample_names[eligible]].host_subject_id.astype(str).to_numpy()
        score=float(np.mean([np.median(err[labels==v]) for v in sorted(set(labels))]))
        delta=score-record['mean_host_label_median_bc']
        if not np.isclose(delta,0,atol=1e-10):
            raise ValueError('independent formula disagrees for study '+str(study))
        rows.append({'study_id':study,'score':score,'difference_vs_report':delta})
    if len(rows)!=reported['scored_studies']:
        raise ValueError('scored study count changed')
    return {'status':'same_viewed_data_independent_arithmetic_reconstruction_only',
            'table_sha256':info['output_sha256'],'metadata_sha256':meta_sha,
            'checked_studies':len(rows),'max_absolute_difference':max(abs(r['difference_vs_report']) for r in rows),
            'note':'Uses a separately written PresenceMean and Bray-Curtis calculation but the same viewed EMP table, metadata and threshold; confirms arithmetic only. Does not qualify external independence, rights, full-community coverage, or a new model beat.',
            'rows':rows}


if __name__=='__main__':
    out=check()
    (ROOT/'results/emp_leave_study_independent_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(out['checked_studies'],out['max_absolute_difference'])
