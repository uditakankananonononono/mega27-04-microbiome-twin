"""Conservative claim gates for patient-level simulation and intervention forecasts."""
from __future__ import annotations


def assess_forecast_request(*, longitudinal_observations, perturbation_labels,
                            external_validation, calibrated_uncertainty,
                            subject_independence, modality_compatible):
    """State which outputs are supported without treating a one-off abundance table as causal data.

    Boolean inputs are evidence checks supplied by a separate validated dataset
    registry, not inferred here from a filename or user-provided title.
    """
    inputs = dict(longitudinal_observations=longitudinal_observations,
                  perturbation_labels=perturbation_labels,
                  external_validation=external_validation,
                  calibrated_uncertainty=calibrated_uncertainty,
                  subject_independence=subject_independence,
                  modality_compatible=modality_compatible)
    if any(type(v) is not bool for v in inputs.values()):
        raise ValueError("all evidence checks must be explicit booleans")
    base = inputs["external_validation"] and inputs["subject_independence"] and inputs["modality_compatible"]
    forecasting = base and inputs["longitudinal_observations"] and inputs["calibrated_uncertainty"]
    intervention = forecasting and inputs["perturbation_labels"]
    missing = [k for k, v in inputs.items() if not v]
    return {"population_prior_research_reference": inputs["modality_compatible"],
            "personalized_trajectory_forecast": forecasting,
            "intervention_direction_forecast": intervention,
            "clinical_treatment_recommendation": False,
            "missing_evidence": missing,
            "note": "Simulation is observational and research-use even when eligible; external intervention tests, not network edges, support direction claims."}
