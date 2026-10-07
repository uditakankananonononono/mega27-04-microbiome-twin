"""Fail-closed metadata screening for a human-gut amplicon benchmark candidate.

This gate NEVER awards final eligibility. Seven-field site amendment is dated
in results/PREREG_20260927_site_gate_amendment.md. Current MGnify experiment-type labels
are insufficient to certify the archived wet-lab method or data-use rights.
"""
from __future__ import annotations

REQUIRED = ('analysis_pagination_complete','uniform_analysis_experiment_type',
            'sample_pagination_complete','old_column_to_analysis_mapped',
            'explicit_human_host_compatible','human_gut_site_compatible','independent_biological_family')


def _validate_record(row):
    if not isinstance(row, dict):
        raise ValueError('source record must be an object')
    study = row.get('study')
    if not isinstance(study, str) or not study or study != study.strip():
        raise ValueError('study identifier must be a nonempty trimmed string')
    for field in REQUIRED:
        value = row.get(field, 'unknown')
        if field == 'uniform_analysis_experiment_type':
            valid = isinstance(value, str) and value in ('amplicon', 'assembly', 'metagenomic', 'unknown')
        else:
            valid = value is None or type(value) is bool or (isinstance(value, str) and value == 'unknown')
        if not valid:
            # Never echo caller values: known fields can accidentally contain
            # participant-level objects, strings, or numeric outcomes.
            raise ValueError(f'invalid value type or label for field {field}')
    return study


def assess_source(row):
    study = _validate_record(row)
    reasons=[]
    for field in REQUIRED:
        value=row.get(field,'unknown')
        expected='amplicon' if field=='uniform_analysis_experiment_type' else True
        if value != expected or (expected is True and value is not True):
            reasons.append({'field':field,'observed':value if value is not None else 'unknown',
                            'required':expected})
    return {'study':study,'decision':'blocked' if reasons else 'metadata_ready_for_manual_review',
            'reasons':reasons,
            'final_external_benchmark_eligible':False,
            'remaining_even_if_metadata_ready':['historical_library_method','source_specific_rights',
               'participant_and_family_lineage','frozen_holdout_and_same_task_benchmark']}


def assess_many(rows):
    rows=list(rows)
    ids=[_validate_record(r) for r in rows]
    if len(ids)!=len(set(ids)):
        raise ValueError('duplicate study identifiers')
    decisions=[assess_source(r) for r in rows]
    return {'candidate_records':len(rows),'blocked':sum(r['decision']=='blocked' for r in decisions),
            'metadata_ready_for_manual_review':sum(r['decision']=='metadata_ready_for_manual_review' for r in decisions),
            'independent_external_benchmark_datasets':0,'records':decisions,
            'scope':'metadata contract only; no biological source family or assay certification; no outcome scores'}
