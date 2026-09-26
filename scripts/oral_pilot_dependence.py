"""Predictive gain diagnostic for the viewed one-study oral transfer pilot.

Person medians are the analysis unit. No causal interaction measurement or
external benchmark verdict can be inferred from this post-pilot analysis.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from microtwin.interaction_score import heldout_scores


def summarize(model='graphtwin'):
    if model not in ('graphtwin','cnode','glv','transformer'):
        raise ValueError('model is not in the viewed pilot')
    source=ROOT/'results/pilot_oral_transfer.json'
    record=json.loads(source.read_text())
    if record['status']!='one_study_debug_pilot_not_external_win' or record['test_people']!=58:
        raise ValueError('unexpected pilot scope or person count')
    a=record['models']['presence_mean']['person_median_errors']
    b=record['models'][model]['person_median_errors']
    ids=sorted(a)
    if set(ids)!=set(b) or len(ids)!=58:
        raise ValueError('unpaired person units')
    score=heldout_scores([a[k] for k in ids],[b[k] for k in ids],
                         ids=ids,groups=['MGYS00002146']*len(ids),n_boot=2000,seed=0)
    # Omits person-level errors and IDs from this derivative; the source pilot
    # retains them for reproduction. A single study has no study-level interval.
    return {'status':'viewed_one_study_predictive_gain_diagnostic',
            'model':model,'source_json_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'people':score['n'],'people_scored':score['n_scored'],
            'fractional_gain_person_median':score['ecosystem_score'],
            'independent_studies':score.get('independent_groups',1),
            'study_level_interval':score['ci95'],
            'interval_status':score.get('interval_status','unavailable'),
            'note':'Gain is a paired predictive error contrast, not causal interaction dependence. One viewed test study, not a source-family benchmark; no independent-study uncertainty.'}


if __name__=='__main__':
    report=[summarize(name) for name in ('graphtwin','cnode','glv','transformer')]
    out=ROOT/'results/oral_pilot_dependence.json'
    out.write_text(json.dumps(report,indent=2)+'\n')
    print([(x['model'],x['fractional_gain_person_median'],x['interval_status']) for x in report])
