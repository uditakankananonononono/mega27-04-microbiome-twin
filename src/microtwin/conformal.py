"""Finite-sample split-conformal Bray-Curtis error radius for a frozen predictor.

Under exchangeability of calibration and test assemblage/outcome pairs,
P(BC(pred, truth) <= radius) >= 1-alpha marginally. If the calibration
sample is too small for a nontrivial bound, return the metric maximum 1.
This is not conditional, cross-source, or intervention uncertainty.
"""
from __future__ import annotations

import math

import numpy as np


def bray_radius(calibration_errors, alpha=0.1):
    if not isinstance(alpha, (int, float)) or isinstance(alpha, bool) or not np.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError('alpha must be strictly between 0 and 1')
    try:
        scores = np.asarray(calibration_errors, dtype=float)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError('finite numeric calibration errors required') from exc
    if scores.ndim != 1 or not len(scores) or not np.isfinite(scores).all():
        raise ValueError('nonempty finite one-dimensional calibration errors required')
    if (scores < 0).any() or (scores > 1 + 1e-10).any():
        raise ValueError('Bray-Curtis errors must be within [0,1]')
    # Accepted floating-point roundoff must not exceed the metric maximum.
    scores = np.minimum(scores, 1.0)
    n = len(scores)
    rank = math.ceil((n + 1) * (1 - alpha))
    radius = 1.0 if rank > n else float(np.sort(scores)[rank - 1])
    return {'radius': radius, 'calibration_samples': n, 'alpha': float(alpha),
            'quantile_rank': rank, 'vacuous': rank > n,
            'scope': 'marginal_exchangeable_within_source_only'}
