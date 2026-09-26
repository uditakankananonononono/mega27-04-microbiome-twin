"""Exact small-cluster uncertainty for descriptive MDSINE2 paired gaps.

These 4/5 mice are related and previously viewed; the bounds do not certify
new-source transfer, model-selection-adjusted performance or a benchmark win.
"""
from __future__ import annotations

from itertools import product
import json
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def mouse_cluster_bounds(cohort, metric, comparator='MDSINE2 (No Modules)'):
    if cohort not in ('healthy','uc') or metric not in ('detected','all'):
        raise ValueError('unknown published cohort or metric')
    inp=ROOT/f'results/mdsine_subject_aggregate_{cohort}_{metric}.json'
    source=json.loads(inp.read_text())
    rows=source['comparisons'][comparator]['per_subject']
    d=np.array([r['median_paired_gap_prior_minus_comparator'] for r in rows])
    if len(d) != source['n_subjects'] or len(set(r['subject'] for r in rows))!=len(d):
        raise ValueError('incomplete or duplicated mouse units')
    # Exact nonparametric cluster bootstrap: enumerate all n**n resamples.
    ix=np.array(list(product(range(len(d)),repeat=len(d))),dtype=int)
    b=d[ix].mean(axis=1)
    return {'cohort':cohort,'metric':metric,'comparator':comparator,
            'mouse_count':len(d),'mouse_deltas':d.tolist(),
            'mean_mouse_median_gap_prior_minus_comparator':float(d.mean()),
            'cluster_bootstrap95':np.quantile(b,[.025,.975]).tolist(),
            'bootstrap_resamples_enumerated':int(len(b)),
            'note':'Exploratory exact mouse-resampling sensitivity of already viewed cohorts. Taxa are NOT independent units; no source-family transfer or multiplicity-adjusted win claim.'}


if __name__=='__main__':
    out=[mouse_cluster_bounds(c,m) for c in ('healthy','uc') for m in ('detected','all')]
    path=ROOT/'results/mdsine_cluster_bounds.json'
    path.write_text(json.dumps(out,indent=2)+'\n')
    for r in out:
        print(r['cohort'],r['metric'],r['mouse_count'],r['mean_mouse_median_gap_prior_minus_comparator'],r['cluster_bootstrap95'])
