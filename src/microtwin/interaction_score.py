"""Held-out predictive interaction-dependence score, not causal necessity.

Inputs are paired errors produced on the same outer held-out samples. The
function cannot score an unlabeled individual who lacks a measured outcome.
"""
from __future__ import annotations

import numpy as np


def _missing_label(label):
    """Guard blank and nonfinite IDs before cluster construction."""
    if label is None or not str(label).strip():
        return True
    if isinstance(label, (float, np.floating)) and not np.isfinite(label):
        return True
    return False


def heldout_scores(prior_error, interaction_error, *, ids=None, groups=None, n_boot=2000, seed=0, eps=1e-12):
    """Return signed fractional improvement and a grouped-bootstrap ecosystem interval.

    A group represents an independent study or subject; when groups are absent,
    samples are assumed independent. The interval describes the median on the
    provided held-out set, not source-transfer validity or model calibration.
    """
    prior = np.asarray(prior_error, dtype=float)
    interaction = np.asarray(interaction_error, dtype=float)
    if prior.ndim != 1 or prior.size == 0 or prior.shape != interaction.shape:
        raise ValueError("errors must be paired, nonempty one-dimensional arrays")
    if not np.isfinite(prior).all() or not np.isfinite(interaction).all() or (prior < 0).any() or (interaction < 0).any():
        raise ValueError("errors must be finite and nonnegative")
    if not isinstance(n_boot, int) or n_boot < 0:
        raise ValueError("n_boot must be a nonnegative integer")
    if not np.isfinite(eps) or eps <= 0:
        raise ValueError("eps must be positive and finite")
    n = len(prior)
    ids = [str(i) for i in range(n)] if ids is None else list(ids)
    if len(ids) != n or any(_missing_label(x) for x in ids):
        raise ValueError("sample ids must be nonempty and aligned with errors")
    ids = list(map(str, ids))
    if len(set(ids)) != n:
        raise ValueError("sample ids must be unique after string normalization")
    groups = ids if groups is None else list(groups)
    if len(groups) != n or any(_missing_label(x) for x in groups):
        raise ValueError("group ids must be nonempty and aligned with errors")
    groups = list(map(str, groups))
    # The fraction is undefined for a zero-error prior. Report no numerical score,
    # rather than hiding a potentially huge denominator behind epsilon.
    valid = prior > eps
    gain = np.full(n, np.nan)
    gain[valid] = (prior[valid] - interaction[valid]) / prior[valid]
    good = np.flatnonzero(valid)
    if not len(good):
        return {"status": "unavailable_no_positive_prior_error", "n": n, "n_scored": 0,
                "n_zero_prior_error": n, "sample_scores": [None] * n, "sample_ids": ids,
                "ecosystem_score": None, "ci95": None, "bootstrap_unit": "group"}
    labels = np.asarray(groups, dtype=object)[good]
    unique = list(dict.fromkeys(labels.tolist()))
    positions = [good[np.flatnonzero(labels == label)] for label in unique]
    rng = np.random.default_rng(seed)
    boot = []
    for _ in range(n_boot if len(unique) >= 2 else 0):
        chosen = rng.integers(len(positions), size=len(positions))
        draw = np.concatenate([positions[i] for i in chosen])
        boot.append(float(np.median(gain[draw])))
    return {"status": "heldout_predictive_score", "n": n, "n_scored": int(len(good)),
            "n_zero_prior_error": int(n - len(good)), "sample_ids": ids,
            "sample_scores": [float(x) if np.isfinite(x) else None for x in gain],
            "ecosystem_score": float(np.median(gain[good])),
            "ci95": [float(x) for x in np.percentile(boot, [2.5, 97.5])] if boot else None,
            "bootstrap_unit": "group", "independent_groups": len(unique),
            "interval_status": "available" if boot else ("insufficient_independent_groups" if len(unique) < 2 else "disabled"),
            "interpretation": "paired outer-held-out predictive gain, not causal interaction necessity"}
