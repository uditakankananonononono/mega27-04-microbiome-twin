"""Viewed-data leave-study-out population-prior development diagnostic.

All 20 candidate studies are already viewed and not certified disjoint from
other source families. This cannot act as a prospective external validation.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from microtwin.data import bray_curtis
from microtwin.models import PresenceMean

TABLE = ROOT / 'data/source_family_candidates/EMP/emp_2k_unambiguous_genus.tsv.gz'
META = ROOT / 'data/source_family_candidates/EMP/emp_mapping_subset_2k.tsv'
INFO = ROOT / 'data/source_family_candidates/EMP/emp_2k_unambiguous_genus_info.json'
META_SHA = '0e4a9d960ec7ccebc0dd4d7de9e4e4ab98abe52aad7f117ea3746d6ab2dd0d39'


def summarize(threshold=.9):
    if not 0 < threshold <= 1:
        raise ValueError('invalid coverage threshold')
    info = json.loads(INFO.read_text())
    if hashlib.sha256(TABLE.read_bytes()).hexdigest() != info['output_sha256']:
        raise ValueError('EMP table checksum mismatch')
    if hashlib.sha256(META.read_bytes()).hexdigest() != META_SHA:
        raise ValueError('EMP metadata checksum mismatch')
    x = pd.read_csv(TABLE, sep='\t', index_col=0)
    meta = pd.read_csv(META, sep='\t', low_memory=False)
    if x.shape != (info['genus_rows'], info['sample_columns']) or not x.columns.is_unique:
        raise ValueError('EMP derivative shape or IDs changed')
    if meta['#SampleID'].duplicated().any() or not set(x.columns) <= set(meta['#SampleID']):
        raise ValueError('EMP metadata join changed')
    m = meta.set_index('#SampleID').loc[x.columns]
    old = set(pd.read_csv(ROOT / 'data/raw/mgnify/manifest.csv').secondary_accession.dropna().astype(str))
    if m.ebi_accession.astype(str).isin(old).any() or m.host_subject_id.isna().any():
        raise ValueError('known old accession or missing subject label')
    if not (m.emp_release1.astype(str).str.lower() == 'true').all() or not (m.qc_filtered.astype(str).str.lower() == 'true').all():
        raise ValueError('candidate flags changed')
    values = x.to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values < 0).any() or (values.sum(axis=0) <= 0).any():
        raise ValueError('invalid genus subset mass')
    studies = []
    for study, rows in m.groupby('study_id'):
        test_idx = x.columns.get_indexer(rows.index)
        if len(test_idx) < 20:
            continue
        people = rows.host_subject_id.astype(str).to_numpy()
        unique = sorted(set(people))
        record = {'study_id': int(study), 'samples': len(test_idx), 'host_labels': len(unique)}
        if len(unique) < 10:
            record['status'] = 'abstained_fewer_than_ten_host_labels'
            studies.append(record)
            continue
        train_idx = np.setdiff1d(np.arange(values.shape[1]), test_idx)
        tr, te = values[:, train_idx].T, values[:, test_idx].T
        covered = tr.sum(axis=0) > 0
        mass = te[:, covered].sum(axis=1) / te.sum(axis=1)
        eligible = mass >= threshold
        record.update({'median_retained_subset_mass_in_train_vocab': float(np.median(mass)),
                       'min_retained_subset_mass_in_train_vocab': float(np.min(mass)),
                       'covered_samples': int(eligible.sum()),
                       'covered_host_labels': len(set(people[eligible]))})
        if not eligible.any():
            record['status'] = 'abstained_zero_covered_samples'
            studies.append(record)
            continue
        ptr = tr / tr.sum(axis=1, keepdims=True)
        pte = te[eligible] / te[eligible].sum(axis=1, keepdims=True)
        ztr = (ptr > 0).astype(float)
        zte = (pte > 0).astype(float)
        pred = PresenceMean().fit(ztr, ptr).predict(zte)
        err = bray_curtis(pred, pte)
        psub = people[eligible]
        person_medians = [np.median(err[psub == s]) for s in sorted(set(psub))]
        # Same eligible test rows, but train only on other host labels within
        # this study. This controls scoring rows, not training-set size or shift.
        within = np.full(len(te), np.nan)
        for label in sorted(set(psub)):
            selected = (people == label) & eligible
            training = people != label
            if training.sum() < 2:
                raise ValueError('insufficient within-study host-label training')
            local = te[training] / te[training].sum(axis=1, keepdims=True)
            local_model = PresenceMean().fit((local > 0).astype(float), local)
            target = te[selected] / te[selected].sum(axis=1, keepdims=True)
            within[selected] = bray_curtis(local_model.predict((target > 0).astype(float)), target)
        if not np.isfinite(within[eligible]).all():
            raise ValueError('within-study comparison incomplete')
        local_medians = [np.median(within[eligible][psub == label]) for label in sorted(set(psub))]
        record.update({'mean_host_label_median_bc': float(np.mean(person_medians)),
                       'same_rows_within_study_mean_host_label_median_bc': float(np.mean(local_medians)),
                       'same_rows_leave_minus_within_bc': float(np.mean(person_medians) - np.mean(local_medians)),
                       'median_sample_bc': float(np.median(err)),
                       'status': 'viewed_leave_study_out_development_only'})
        studies.append(record)
    scored = [r for r in studies if r['status'].startswith('viewed_leave')]
    return {'status': 'viewed_emp_leave_study_out_development_not_external_benchmark',
            'table_sha256': info['output_sha256'], 'metadata_sha256': META_SHA,
            'threshold_on_retained_genus_subset': threshold,
            'candidate_studies': len(studies), 'scored_studies': len(scored),
            'covered_samples': sum(r['covered_samples'] for r in scored),
            'median_of_study_mean_host_label_medians': float(np.median([r['mean_host_label_median_bc'] for r in scored])) if scored else None,
            'study_results': studies,
            'note': 'All candidate studies have been viewed for method development, and mirror/biological-unit eligibility is incomplete. Train/test are disjoint EMP study IDs in this derivative, NOT untouched source families. Coverage is relative to an already heavily filtered genus subset (median 32.06% raw BIOM mass), not full-community coverage. Scores renormalize retained genera, include no same-task top comparator or multiplicity adjustment, and cannot establish the requested external win.'}


if __name__ == '__main__':
    result = summarize()
    dest = ROOT / 'results/emp_leave_study_development.json'
    dest.write_text(json.dumps(result, indent=2) + '\n')
    print(result['scored_studies'], result['covered_samples'], result['median_of_study_mean_host_label_medians'])
