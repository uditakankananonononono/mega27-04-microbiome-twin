"""Evaluate direction-of-change forecasts against labeled perturbation outcomes."""
from __future__ import annotations

import numpy as np


def direction_accuracy(predicted_change, observed_change, *, groups, threshold=0.0):
    """Score only independently labeled, nontrivial changes.

    Observational co-occurrence is not an intervention label. Excludes observed
    changes within the prespecified absolute threshold; zero predictions are
    abstentions, never silently scored as a correct direction.
    """
    p = np.asarray(predicted_change, float)
    y = np.asarray(observed_change, float)
    g = list(groups)
    if p.ndim != 1 or y.shape != p.shape or not len(p) or len(g) != len(p):
        raise ValueError("aligned nonempty one-dimensional changes and groups required")
    if not np.isfinite(p).all() or not np.isfinite(y).all() or threshold < 0 or not np.isfinite(threshold):
        raise ValueError("finite changes and nonnegative threshold required")
    if any(v is None or str(v).strip() == "" for v in g):
        raise ValueError("intervention experiment group required")
    eligible = np.abs(y) > threshold
    attempted = eligible & (p != 0)
    if not attempted.any():
        return {"status": "unavailable_no_scored_directions", "eligible": int(eligible.sum()),
                "attempted": 0, "accuracy": None, "coverage": 0.0}
    return {"status": "labeled_perturbation_only", "eligible": int(eligible.sum()),
            "attempted": int(attempted.sum()),
            "accuracy": float((np.sign(p[attempted]) == np.sign(y[attempted])).mean()),
            "coverage": float(attempted.sum()/max(int(eligible.sum()),1)),
            "independent_experiment_groups": len(set(np.asarray(g,dtype=object)[attempted])),
            "note": "Direction agreement is not proof of a causal interaction network."}
