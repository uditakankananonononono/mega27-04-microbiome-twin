"""Source-level and design-level fail-closed result declaration gate.

A checked box is not proof: records must cite independently inspected source
and test evidence. No code can certify novelty or fairness from booleans alone.
"""
from __future__ import annotations


def claim_readiness(*, manifest, evaluation, discovery):
    """Make missing gates explicit and prohibit success from benchmark p-values alone.

    This guard is deliberately conservative. Evidence references are opaque
    but required; a real reviewer must still inspect the cited artifacts.
    """
    if not all(isinstance(x,dict) for x in (manifest,evaluation,discovery)):
        raise ValueError('manifest, evaluation and discovery evidence records required')
    checks={
        'heldout_source_independence':(manifest,'heldout_source_independence'),
        'subject_disjoint':(manifest,'subject_disjoint'),
        'taxonomy_and_assay_compatible':(manifest,'taxonomy_and_assay_compatible'),
        'rights_reviewed':(manifest,'rights_reviewed'),
        'protocol_frozen_before_outcomes':(evaluation,'protocol_frozen_before_outcomes'),
        'same_task_eligible_comparator':(evaluation,'same_task_eligible_comparator'),
        'study_level_interval_beats_comparator':(evaluation,'study_level_interval_beats_comparator'),
        'multiplicity_controlled':(evaluation,'multiplicity_controlled'),
        'new_claim_vs_prior_art':(discovery,'new_claim_vs_prior_art'),
        'independent_replication':(discovery,'independent_replication'),
    }
    missing=[]
    for label,(record,key) in checks.items():
        item=record.get(key)
        if not isinstance(item,dict) or item.get('passed') is not True or not isinstance(item.get('evidence'),str) or not item['evidence'].strip():
            missing.append(label)
    return {'status':'requires_human_evidence_review_even_if_all_fields_pass' if not missing else 'claim_blocked',
            'ready_for_manual_review':not missing,'unmet_gates':missing,
            'can_auto_claim_discovery_and_benchmark_win':False,
            'note':'Structured evidence cannot authenticate source independence, rights, biological novelty, or comparator quality. Manual verification is required before any public claim.'}
