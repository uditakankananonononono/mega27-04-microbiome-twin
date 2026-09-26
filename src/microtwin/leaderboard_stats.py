"""Study-aware paired comparison for an untouched external-source leaderboard."""
from __future__ import annotations

import numpy as np


def compare_by_study(candidate, baseline, study_ids, *, n_boot=5000, seed=0):
    """Macro-average study median errors, then bootstrap independent studies.

    Negative candidate-minus-baseline delta favors candidate. A win requires
    a 95% interval entirely below zero and at least two independent studies.
    Samples within a study remain together in each bootstrap draw.
    """
    c = np.asarray(candidate, float)
    b = np.asarray(baseline, float)
    ids = list(study_ids)
    if c.ndim != 1 or b.shape != c.shape or len(ids) != len(c) or not len(c):
        raise ValueError("paired nonempty sample errors and aligned study IDs required")
    if not np.isfinite(c).all() or not np.isfinite(b).all() or (c < 0).any() or (b < 0).any():
        raise ValueError("finite nonnegative errors required")
    if any(x is None or str(x).strip() == "" for x in ids):
        raise ValueError("each row needs a study ID")
    if not isinstance(n_boot, int) or n_boot < 0:
        raise ValueError("n_boot must be a nonnegative integer")
    unique = list(dict.fromkeys(ids))
    c_study = np.array([np.median(c[np.asarray(ids) == sid]) for sid in unique])
    b_study = np.array([np.median(b[np.asarray(ids) == sid]) for sid in unique])
    d = c_study - b_study
    macro = float(d.mean())
    ci = None
    if len(unique) >= 2 and n_boot:
        rng = np.random.default_rng(seed)
        ix = rng.integers(len(unique), size=(n_boot, len(unique)))
        ci = [float(v) for v in np.quantile(d[ix].mean(1), [0.025, 0.975])]
    verdict = "insufficient_independent_studies" if len(unique) < 2 else (
        "interval_disabled" if ci is None else
        "WIN" if ci[1] < 0 else "LOSS" if ci[0] > 0 else "tie_or_uncertain")
    return {"n_samples": len(c), "n_studies": len(unique),
            "macro_median_candidate": float(c_study.mean()),
            "macro_median_baseline": float(b_study.mean()),
            "delta_candidate_minus_baseline": macro, "ci95_study_bootstrap": ci,
            "verdict": verdict, "study_deltas": dict(zip(map(str, unique), map(float, d)))}
