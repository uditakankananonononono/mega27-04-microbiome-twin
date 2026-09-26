from microtwin.forecast_eligibility import assess_forecast_request


def test_cross_sectional_patient_table_cannot_trigger_intervention_claim():
    result = assess_forecast_request(longitudinal_observations=False, perturbation_labels=False,
                                     external_validation=False, calibrated_uncertainty=False,
                                     subject_independence=False, modality_compatible=True)
    assert result["population_prior_research_reference"]
    assert not result["personalized_trajectory_forecast"]
    assert not result["intervention_direction_forecast"]


def test_longitudinal_without_perturbation_labels_still_abstains_on_intervention():
    result = assess_forecast_request(longitudinal_observations=True, perturbation_labels=False,
                                     external_validation=True, calibrated_uncertainty=True,
                                     subject_independence=True, modality_compatible=True)
    assert result["personalized_trajectory_forecast"]
    assert not result["intervention_direction_forecast"]
    assert not result["clinical_treatment_recommendation"]
