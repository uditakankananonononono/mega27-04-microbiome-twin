"""Preflight paired longitudinal perturbation design without abundance outcomes.

This checks whether cohort labels and time windows can support a comparison.
It does not infer antibiotic, diet or species-removal effects.
"""
from __future__ import annotations

from collections import defaultdict
import math


def screen_paired_design(records, *, baseline_end=0, followup_start=1,
                         minimum_subjects_per_arm=2):
    """Require explicit study, subject, sample, arm, time and phase on every row.

    Baseline/follow-up windows are caller-specified before outcomes. A phase is
    part of the subject key to avoid treating phases as independent datasets.
    Control and intervention arms must each have paired subjects in a phase.
    """
    if not math.isfinite(baseline_end) or not math.isfinite(followup_start) or baseline_end >= followup_start:
        raise ValueError('separated finite baseline/follow-up windows required')
    if not isinstance(minimum_subjects_per_arm,int) or minimum_subjects_per_arm < 2:
        raise ValueError('minimum subjects per arm must be at least two')
    rows = list(records)
    if not rows:
        raise ValueError('nonempty design records required')
    required=('study','phase','subject','sample','arm','time')
    samples=set()
    by_subject=defaultdict(lambda:{'times':[],'arms':set(),'samples':[]})
    by_study_subject=defaultdict(set)
    for i,row in enumerate(rows):
        if not isinstance(row,dict) or any(k not in row for k in required):
            raise ValueError(f'row {i}: missing design field')
        labels=[str(row[k]).strip() if row[k] is not None else '' for k in required[:-1]]
        if any(not v for v in labels) or labels[4] not in ('intervention','control'):
            raise ValueError(f'row {i}: invalid or missing labels')
        t=row['time']
        if isinstance(t,bool) or not isinstance(t,(int,float)) or not math.isfinite(t):
            raise ValueError(f'row {i}: invalid time')
        study,phase,subject,sample,arm=labels
        if sample in samples:raise ValueError('duplicate sample ID')
        samples.add(sample)
        key=(study,phase,subject)
        by_subject[key]['times'].append(float(t))
        by_subject[key]['arms'].add(arm)
        by_subject[key]['samples'].append(sample)
        by_study_subject[subject].add(study)
    if any(len(studies)>1 for studies in by_study_subject.values()):
        raise ValueError('subject label appears in multiple studies; namespace or reconcile identities')
    phases=defaultdict(lambda:{'intervention':0,'control':0,'unpaired':0})
    for (study,phase,subject),info in by_subject.items():
        if len(info['arms'])!=1:raise ValueError('subject switches intervention arm')
        if len(info['times'])!=len(set(info['times'])):raise ValueError('duplicate subject/timepoint')
        paired=any(t<=baseline_end for t in info['times']) and any(t>=followup_start for t in info['times'])
        p=phases[(study,phase)]
        if paired:p[next(iter(info['arms']))]+=1
        else:p['unpaired']+=1
    summary=[{'study':study,'phase':phase,'paired_intervention_subjects':p['intervention'],
              'paired_control_subjects':p['control'],'unpaired_subjects':p['unpaired'],
              'eligible_on_design_only':min(p['intervention'],p['control'])>=minimum_subjects_per_arm}
             for (study,phase),p in sorted(phases.items())]
    return {'status':'design_screen_only_no_outcomes','samples':len(samples),
            'subjects_study_phase_keys':len(by_subject),'phases':summary,
            'eligible_phases_on_design_only':sum(p['eligible_on_design_only'] for p in summary),
            'note':'Paired labels do not establish treatment causality, outcome QC, balanced timing, source independence, data-use rights or a trained forecast. Phases within one study are not independent external datasets.'}
