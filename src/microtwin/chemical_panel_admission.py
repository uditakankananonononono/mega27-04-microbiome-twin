"""Aggregate missingness-aware specimen eligibility, not outcome-value analysis."""
from collections import Counter, defaultdict
from math import isfinite


def screen_chemical_panel(samples, *, analytes, units_verified, min_per_phase=3):
    """Inspect explicit observed flags only; caller owns assay/sentinel provenance."""
    if type(units_verified) is not bool:
        raise ValueError('units_verified must be an explicit boolean')
    if type(min_per_phase) is not int or min_per_phase < 1:
        raise ValueError('positive integer min_per_phase required')
    if not isinstance(analytes, (list, tuple)) or not analytes or any(type(a) is not str or not a.strip() for a in analytes) or len(set(analytes)) != len(analytes):
        raise ValueError('distinct nonempty analytes required')
    required={'sample','source_family','subject','arm','phase','time','observed'}
    by_subject=defaultdict(list)
    sample_ids=set()
    coordinates=set()
    for row in samples:
        if not isinstance(row,dict) or set(row)!=required:
            raise ValueError('only explicit metadata and observed flags accepted, no outcome fields')
        for k in ['sample','source_family','subject','arm']:
            if type(row[k]) is not str or not row[k].strip():
                raise ValueError('nonempty string metadata required')
        if row['phase'] not in ('before','during'):
            raise ValueError('phase must be before or during')
        if isinstance(row['time'],bool) or not isinstance(row['time'],(int,float)) or not isfinite(row['time']):
            raise ValueError('finite numeric collection time required')
        observed=row['observed']
        if not isinstance(observed,dict) or set(observed)!=set(analytes) or any(type(v) is not bool for v in observed.values()):
            raise ValueError('exact analyte observed boolean map required')
        sample_key=(row['source_family'],row['sample'])
        key=(row['source_family'],row['subject'])
        coord=(key,row['time'])
        if sample_key in sample_ids or coord in coordinates:
            raise ValueError('duplicate specimen or source-subject-time; resolve technical replicates')
        sample_ids.add(sample_key)
        coordinates.add(coord)
        by_subject[key].append(row)
    if not by_subject:
        raise ValueError('samples required')
    eligible=Counter({a:0 for a in analytes})
    joint=0;complete_panel=0;arm_conflicts=0;temporal_blocks=0
    for rows in by_subject.values():
        if len({r['arm'] for r in rows})!=1:
            arm_conflicts+=1
            continue
        before=[r for r in rows if r['phase']=='before']
        during=[r for r in rows if r['phase']=='during']
        if not before or not during or max(r['time'] for r in before)>=min(r['time'] for r in during):
            temporal_blocks+=1
            continue
        flags={a:all(sum(r['observed'][a] for r in phase)>=min_per_phase for phase in (before,during)) for a in analytes}
        for a,ok in flags.items():eligible[a]+=int(ok)
        joint+=int(all(flags.values()))
        complete_panel+=int(all(sum(all(r['observed'][a] for a in analytes) for r in phase)>=min_per_phase for phase in (before,during)))
    return {'status':'metadata_eligible' if units_verified and joint>0 else 'abstain',
            'units_verified':units_verified,'source_subject_keys':len(by_subject),
            'sample_rows':len(sample_ids),'min_per_phase':min_per_phase,
            'subjects_with_arm_conflict':arm_conflicts,'subjects_with_temporal_block':temporal_blocks,
            'per_analyte_paired_eligible_subjects':dict(eligible),
            'joint_analyte_eligible_subjects':joint,'complete_specimen_panel_eligible_subjects':complete_panel,
            'outcome_values_consumed':False,'independent_validation':False,
            'forecast_authorized':False,'clinical_eligible':False,
            'note':'Flag eligibility is not assay QC, rights, independent recruitment, or validated forecasting. Counts remain descriptive when units are unverified.'}
