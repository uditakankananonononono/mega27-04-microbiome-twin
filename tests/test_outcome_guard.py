from microtwin.outcome_guard import claim_readiness


def test_missing_references_fail_closed():
    r=claim_readiness(manifest={'heldout_source_independence':{'passed':True,'evidence':''}},evaluation={},discovery={})
    assert r['status']=='claim_blocked' and 'heldout_source_independence' in r['unmet_gates']
    assert not r['can_auto_claim_discovery_and_benchmark_win']


def test_even_all_self_reported_passes_need_manual_review():
    m=['heldout_source_independence','subject_disjoint','taxonomy_and_assay_compatible','rights_reviewed']
    e=['protocol_frozen_before_outcomes','same_task_eligible_comparator','study_level_interval_beats_comparator','multiplicity_controlled']
    d=['new_claim_vs_prior_art','independent_replication']
    def records(keys):return {key:{'passed':True,'evidence':'https://example.org/checked'} for key in keys}
    r=claim_readiness(manifest=records(m),evaluation=records(e),discovery=records(d))
    assert r['ready_for_manual_review'] and not r['can_auto_claim_discovery_and_benchmark_win']
