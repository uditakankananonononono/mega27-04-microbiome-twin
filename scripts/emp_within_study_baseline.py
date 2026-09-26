"""Exploratory within-study population-prior errors on viewed EMP subset.

This is a real-data calculation, not source transfer: each study trains and
scores internally, source taxonomy is Greengenes, and raw mass retention is low.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from microtwin.data import bray_curtis
from microtwin.models import PresenceMean

TABLE=ROOT/'data/source_family_candidates/EMP/emp_2k_unambiguous_genus.tsv.gz'
META=ROOT/'data/source_family_candidates/EMP/emp_mapping_subset_2k.tsv'
INFO=ROOT/'data/source_family_candidates/EMP/emp_2k_unambiguous_genus_info.json'


def summarize():
    info=json.loads(INFO.read_text())
    expected_metadata_sha256='0e4a9d960ec7ccebc0dd4d7de9e4e4ab98abe52aad7f117ea3746d6ab2dd0d39'
    if hashlib.sha256(META.read_bytes()).hexdigest()!=expected_metadata_sha256:
        raise ValueError('EMP metadata checksum mismatch')
    if hashlib.sha256(TABLE.read_bytes()).hexdigest()!=info['output_sha256']:
        raise ValueError('candidate table checksum mismatch')
    x=pd.read_csv(TABLE,sep='\t',index_col=0)
    meta=pd.read_csv(META,sep='\t',low_memory=False)
    if x.shape!=(info['genus_rows'],info['sample_columns']) or not x.columns.is_unique:
        raise ValueError('candidate shape or IDs differ')
    if meta['#SampleID'].duplicated().any() or not set(x.columns)<=set(meta['#SampleID']):
        raise ValueError('metadata/sample map incomplete')
    m=meta.set_index('#SampleID').loc[x.columns]
    old=set(pd.read_csv(ROOT/'data/raw/mgnify/manifest.csv').secondary_accession.dropna().astype(str))
    if m.ebi_accession.astype(str).isin(old).any() or m.host_subject_id.isna().any():
        raise ValueError('known old accession or missing subject ID in candidate')
    if not (m['emp_release1'].astype(str).str.lower()=='true').all() or not (m['qc_filtered'].astype(str).str.lower()=='true').all():
        raise ValueError('EMP release/QC flags missing in candidate')
    if (x.to_numpy()<0).any() or not np.isfinite(x.to_numpy()).all():
        raise ValueError('invalid abundance table')
    studies=[]
    for study, rows in m.groupby('study_id'):
        cols=rows.index.tolist()
        if len(cols)<20:continue
        p=x[cols].T.to_numpy(float)
        if (p.sum(1)<=0).any():raise ValueError('zero named-genus mass')
        p/=p.sum(1,keepdims=True)
        z=(p>0).astype(float)
        subjects=rows.host_subject_id.astype(str).tolist()
        unique=sorted(set(subjects))
        if len(unique)<10:
            studies.append({'study_id':int(study),'samples':len(cols),'subjects':len(unique),
                            'status':'abstained_fewer_than_ten_subjects'})
            continue
        errors=[]
        per_subject=[]
        for subject in unique:
            test=np.array([s==subject for s in subjects])
            train=~test
            if train.sum()<2:raise ValueError('insufficient train samples')
            pred=PresenceMean().fit(z[train],p[train]).predict(z[test])
            e=bray_curtis(pred,p[test])
            errors.extend(e.tolist())
            per_subject.append(float(np.median(e)))
        studies.append({'study_id':int(study),'samples':len(cols),'subjects':len(unique),
                        'median_sample_bc':float(np.median(errors)),
                        'mean_subject_median_bc':float(np.mean(per_subject)),
                        'status':'within_study_leave_subject_out_development_only'})
    eligible=[r for r in studies if r['status'].startswith('within_study')]
    return {'status':'viewed_emp_within_study_baseline_not_external_transfer',
            'table_sha256':info['output_sha256'],'metadata_sha256':expected_metadata_sha256,
            'candidate_studies':len(studies),'scored_studies':len(eligible),
            'scored_samples':sum(r['samples'] for r in eligible),
            'scored_study_subject_labels':sum(r['subjects'] for r in eligible),
            'median_of_study_mean_subject_medians':float(np.median([r['mean_subject_median_bc'] for r in eligible])) if eligible else None,
            'study_results':studies,
            'note':'Greengenes named-unambiguous genus subset, median 32.06% raw count mass retained (min 0.21%); development-only leave-host_subject_id-out WITHIN study, no source holdout, no top-tool comparison, no external transfer or biological discovery. Host IDs may be ecological units, not people; per-study counts are labels, not validated independent biological subjects.'}


if __name__=='__main__':
    report=summarize()
    out=ROOT/'results/emp_within_study_baseline.json'
    out.write_text(json.dumps(report,indent=2)+'\n')
    print(report['candidate_studies'],report['scored_studies'],report['median_of_study_mean_subject_medians'])
