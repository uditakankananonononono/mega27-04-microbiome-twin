"""Person-unit paired sensitivity on the already viewed one-study oral pilot.

Descriptive only. The model family and study have been inspected, so this is
not an untouched final source test, independent replication or winner test.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'results/pilot_oral_transfer.json'
NBOOT=10000


def summarize(seed=0):
    pilot=json.loads(SOURCE.read_text())
    if pilot['status']!='one_study_debug_pilot_not_external_win':
        raise ValueError('unexpected pilot scope')
    models=pilot['models']
    if any(v['status']!='ok' for v in models.values()):
        raise ValueError('incomplete model fits')
    base=models['presence_mean']['person_median_errors']
    ids=sorted(base)
    if len(ids)!=pilot['test_people'] or any(set(v['person_median_errors'])!=set(ids) for v in models.values()):
        raise ValueError('subject-unit mismatch')
    rng=np.random.default_rng(seed)
    # One shared resample schedule across comparators, with the whole person
    # rather than each oral site as the bootstrap unit.
    ix=rng.integers(0,len(ids),size=(NBOOT,len(ids)))
    out={'status':'viewed_one_study_person_sensitivity_not_final_benchmark',
         'source_json_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
         'test_people':len(ids),'bootstrap_unit':'person','bootstrap_resamples':NBOOT,'seed':seed,
         'base':'presence_mean','comparisons':{},
         'note':'Same viewed source, 20 train sites, model family selected after earlier pilots. Person resampling cannot create new independent studies, validate taxonomy/rights or prove a top-tool win.'}
    a=np.array([base[x] for x in ids])
    for model,v in models.items():
        if model=='presence_mean':continue
        b=np.array([v['person_median_errors'][x] for x in ids])
        diff=b-a
        # The locked original protocol uses the mean across persons of their
        # site-median errors. A median across persons is a different target.
        boot=np.mean(b[ix]-a[ix],axis=1)
        locked_a=float(np.mean(a))
        locked_b=float(np.mean(b))
        if not np.isclose(locked_a,models['presence_mean']['macro_person_median_bray_curtis']) or not np.isclose(locked_b,v['macro_person_median_bray_curtis']):
            raise ValueError('person mean does not match locked pilot metric')
        out['comparisons'][model]={'mean_person_site_median_model':locked_b,
                                   'mean_person_site_median_prior':locked_a,
                                   'locked_metric_delta_model_minus_prior':float(np.mean(diff)),
                                   'person_resample95_locked_metric':np.quantile(boot,[.025,.975]).tolist(),
                                   'posthoc_median_across_people_delta_model_minus_prior':float(np.median(b)-np.median(a)),
                                   'median_paired_person_gap_model_minus_prior':float(np.median(diff)),
                                   'people_model_better':int((diff<0).sum()),
                                   'people_prior_better':int((diff>0).sum()),
                                   'people_tied':int((diff==0).sum())}
    return out


if __name__=='__main__':
    output=summarize()
    dest=ROOT/'results/oral_pilot_person_sensitivity.json'
    dest.write_text(json.dumps(output,indent=2)+'\n')
    for name,r in output['comparisons'].items():
        print(name,r['locked_metric_delta_model_minus_prior'],r['person_resample95_locked_metric'])
