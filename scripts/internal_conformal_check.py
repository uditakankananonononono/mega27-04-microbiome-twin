"""Internal held-out coverage of the population predictor on six archived tables.

One seeded 60/20/20 split per ecosystem after assemblage dedup. No use of
held-out truth in training or calibration; no source or person holdout.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from microtwin.conformal import bray_radius
from microtwin.data import DATASETS, bray_curtis, load
from microtwin.models import PresenceMean


def evaluate(name, *, seed=0, alpha=0.1):
    if name not in DATASETS:
        raise ValueError('unknown archived dataset')
    z, p = load(name)
    n = len(z)
    order = np.random.default_rng(seed).permutation(n)
    n_train = int(.6 * n)
    n_cal = int(.2 * n)
    if min(n_train, n_cal, n - n_train - n_cal) < 1:
        raise ValueError('insufficient data for disjoint three-way split')
    tr, cal, te = order[:n_train], order[n_train:n_train+n_cal], order[n_train+n_cal:]
    model = PresenceMean().fit(z[tr], p[tr])
    cal_errors = bray_curtis(model.predict(z[cal]), p[cal])
    test_errors = bray_curtis(model.predict(z[te]), p[te])
    bound = bray_radius(cal_errors, alpha)
    source = ROOT / 'data/raw/cnode' / f'{name}.csv'
    return {'dataset': name, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'train': len(tr), 'calibration': len(cal), 'test': len(te),
            'radius': bound['radius'], 'quantile_rank': bound['quantile_rank'],
            'vacuous': bound['vacuous'], 'covered_test': int(np.sum(test_errors <= bound['radius'])),
            'empirical_coverage': float(np.mean(test_errors <= bound['radius'])),
            'test_mean_error': float(np.mean(test_errors)),
            'test_median_error': float(np.median(test_errors)),
            'max_test_error': float(np.max(test_errors))}


if __name__ == '__main__':
    rows = [evaluate(name) for name in DATASETS]
    result = {'status': 'internal_same_dataset_split_not_external_calibration',
              'model': 'PresenceMean', 'alpha': .1, 'seed': 0,
              'split': '60 percent train, floor 20 percent calibration, remaining test after assemblage dedup',
              'rows': rows,
              'note': 'Finite-sample 90% marginal coverage only under calibration/test exchangeability; per-ecosystem held-out rates are descriptive and may be lower than 90%. Dataset sources have already been viewed. No cross-source, personalized, clinical, or intervention uncertainty; no calibrated TRI.'}
    out = ROOT / 'results/internal_conformal_check.json'
    out.write_text(json.dumps(result, indent=2) + '\n')
    for x in rows:
        print(x['dataset'], x['calibration'], x['test'], x['radius'], x['covered_test'], x['empirical_coverage'])
