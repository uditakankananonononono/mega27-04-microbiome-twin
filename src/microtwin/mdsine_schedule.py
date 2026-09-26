"""Map MDSINE2 Figure 3 timepoint indices to the published raw schedule.

The original preprocessing removes times 0 and 0.5. This map reads no held-out
abundance or qPCR and fails if source schedule length does not match the figure.
"""
from __future__ import annotations

import numpy as np


def scheduled_days(sample_times, n_timepoints):
    times = np.asarray(sample_times, dtype=float)
    if times.ndim != 1 or not np.isfinite(times).all() or len(np.unique(times)) != len(times):
        raise ValueError('finite, unique sample times required')
    if not isinstance(n_timepoints, int) or n_timepoints < 1:
        raise ValueError('positive timepoint count required')
    remaining = np.sort(times[times >= 1.0])
    if len(remaining) != n_timepoints:
        raise ValueError('figure and post-preprocessing source schedule length disagree')
    return remaining
