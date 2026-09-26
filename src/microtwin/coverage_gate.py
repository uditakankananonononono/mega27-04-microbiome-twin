"""Fixed-vocabulary abstention before applying a source-transfer predictor."""
from __future__ import annotations

import math


def coverage_gate(coverage, *, min_mass=0.9, min_shared_genera=20):
    """Return eligibility based only on source inputs, not observed outcomes.

    Thresholds are defaults for a prospective pilot, not calibrated biological
    cutoffs. Freeze in the benchmark manifest before opening test predictions.
    """
    if (not isinstance(min_mass, (int, float)) or isinstance(min_mass, bool) or
            not math.isfinite(min_mass) or not 0 <= min_mass <= 1 or
            not isinstance(min_shared_genera, int) or isinstance(min_shared_genera, bool) or
            min_shared_genera < 1):
        raise ValueError("invalid thresholds")
    if not isinstance(coverage, dict):
        raise ValueError("validated vocabulary coverage report required")
    n=coverage.get("shared_genera")
    low=coverage.get("minimum_test_mass_covered")
    if (not isinstance(n, int) or isinstance(n, bool) or
            not isinstance(low, (int, float)) or isinstance(low, bool) or
            not math.isfinite(low) or not 0 <= low <= 1):
        raise ValueError("validated vocabulary coverage report required")
    reasons=[]
    if n < min_shared_genera:reasons.append("too_few_shared_genera")
    if low < min_mass:reasons.append("low_sample_vocabulary_coverage")
    return {"eligible_on_vocabulary_only":not reasons,"reasons":reasons,
            "thresholds":{"minimum_sample_mass":min_mass,"minimum_shared_genera":min_shared_genera},
            "note":"This does not verify labels, taxonomy synonyms, subject independence or license."}
