"""Post-hoc paired-site diagnostic on the already viewed oral pilot.

D/H are site labels on the same diseased person, not intervention labels.
These descriptive differences do not imply causal or external-source effects.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / 'results/pilot_oral_transfer.json'
SUBJECTS = ROOT / 'data/external_candidate/MGYS00002146_subject_map.json'


def summarize(seed=2026, resamples=10000):
    pilot = json.loads(PILOT.read_text())
    subject_map = json.loads(SUBJECTS.read_text())['mapping']
    if pilot['status'] != 'one_study_debug_pilot_not_external_win':
        raise ValueError('unexpected pilot scope')
    site_ids = set(pilot['models']['presence_mean']['site_errors'])
    if site_ids != set(subject_map) or len(site_ids) != 87:
        raise ValueError('sample mapping mismatch')
    pairs = {}
    for sample, unit in subject_map.items():
        person = unit['subject']
        site = unit['site']
        if site not in ('D', 'H') or site in pairs.setdefault(person, {}):
            raise ValueError('missing or duplicate site label')
        pairs[person][site] = sample
    paired = sorted(k for k, v in pairs.items() if set(v) == {'D', 'H'})
    if len(paired) != 29 or len(pairs) != 58:
        raise ValueError('unexpected biological units')
    rng = np.random.default_rng(seed)
    draw = rng.integers(0, len(paired), size=(resamples, len(paired)))
    out = {
        'status': 'posthoc_viewed_one_study_paired_site_diagnostic',
        'pilot_sha256': hashlib.sha256(PILOT.read_bytes()).hexdigest(),
        'subject_map_sha256': hashlib.sha256(SUBJECTS.read_bytes()).hexdigest(),
        'paired_people': len(paired), 'total_people': len(pairs),
        'bootstrap_unit': 'paired person', 'resamples': resamples, 'seed': seed,
        'models': {},
        'scope': 'Same viewed oral study. D/H are paired oral sites on diseased people, not an intervention or independent source. Exploratory, no multiplicity correction.',
    }
    baseline = pilot['models']['presence_mean']['site_errors']
    prior_gap = np.array([baseline[pairs[k]['D']] - baseline[pairs[k]['H']] for k in paired])
    for name, result in pilot['models'].items():
        if result['status'] != 'ok' or set(result['site_errors']) != site_ids:
            raise ValueError('incomplete model output')
        err = result['site_errors']
        d_minus_h = np.array([err[pairs[k]['D']] - err[pairs[k]['H']] for k in paired])
        contrast = d_minus_h - prior_gap
        out['models'][name] = {
            'mean_D_minus_H_error': float(np.mean(d_minus_h)),
            'median_D_minus_H_error': float(np.median(d_minus_h)),
            'people_D_higher_error': int(np.sum(d_minus_h > 0)),
            'bootstrap95_mean_D_minus_H': np.quantile(np.mean(d_minus_h[draw], axis=1), [.025, .975]).tolist(),
            'interaction_contrast_D_minus_H_vs_prior': float(np.mean(contrast)),
            'bootstrap95_interaction_contrast': np.quantile(np.mean(contrast[draw], axis=1), [.025, .975]).tolist(),
        }
    return out


if __name__ == '__main__':
    output = summarize()
    (ROOT / 'results/oral_paired_site_diagnostic.json').write_text(json.dumps(output, indent=2) + '\n')
    for name, row in output['models'].items():
        print(name, row['mean_D_minus_H_error'], row['bootstrap95_mean_D_minus_H'])
