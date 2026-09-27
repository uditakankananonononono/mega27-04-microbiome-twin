"""Evaluate direction-of-change forecasts against labeled perturbation outcomes."""
from __future__ import annotations

import numpy as np


def direction_accuracy(predicted_change, observed_change, *, groups, threshold=0.0, n_boot=2000, seed=0):
    """Score only independently labeled, nontrivial changes.

    Observational co-occurrence is not an intervention label. Excludes observed
    changes within the prespecified absolute threshold; zero predictions are
    abstentions, never silently scored as a correct direction.
    """
    if type(n_boot) is not int or not 1 <= n_boot <= 10000 or type(seed) is not int or seed < 0:
        raise ValueError("n_boot must be 1..10000 and seed a nonnegative integer")
    p = np.asarray(predicted_change, float)
    y = np.asarray(observed_change, float)
    g = list(groups)
    if p.ndim != 1 or y.shape != p.shape or not len(p) or len(g) != len(p):
        raise ValueError("aligned nonempty one-dimensional changes and groups required")
    if not np.isfinite(p).all() or not np.isfinite(y).all() or threshold < 0 or not np.isfinite(threshold):
        raise ValueError("finite changes and nonnegative threshold required")
    if any(v is None or not str(v).strip() or
           (isinstance(v, (float, np.floating)) and not np.isfinite(v)) for v in g):
        raise ValueError("intervention experiment group required")
    g = list(map(str, g))
    eligible = np.abs(y) > threshold
    attempted = eligible & (p != 0)
    if not attempted.any():
        return {"status": "unavailable_no_scored_directions", "eligible": int(eligible.sum()),
                "attempted": 0, "accuracy": None, "coverage": 0.0,
                "group_macro_accuracy": None, "group_bootstrap_95ci": None,
                "attempted_group_summaries": [], "independent_experiment_groups": 0}
    group_summaries=[]
    for label in sorted(set(g)):
        member=np.asarray([v==label for v in g],bool)
        n=int((attempted & member).sum())
        if not n:continue
        eligible_group=int((eligible & member).sum())
        score=float((np.sign(p[attempted & member])==np.sign(y[attempted & member])).mean())
        group_summaries.append({"eligible":eligible_group,"attempted":n,
                                "accuracy":score,"coverage":n/eligible_group})
    scores=np.asarray([x['accuracy'] for x in group_summaries],float)
    macro=float(scores.mean())
    ci=None
    if len(scores)>=2:
        rng=np.random.default_rng(seed)
        draws=np.mean(scores[rng.integers(0,len(scores),size=(n_boot,len(scores)))],axis=1)
        ci=[float(v) for v in np.quantile(draws,[.025,.975])]
    return {"status": "labeled_perturbation_only", "eligible": int(eligible.sum()),
            "attempted": int(attempted.sum()),
            "accuracy": float((np.sign(p[attempted]) == np.sign(y[attempted])).mean()),
            "coverage": float(attempted.sum()/max(int(eligible.sum()),1)),
            "independent_experiment_groups": len(scores),
            "group_macro_accuracy":macro,"group_bootstrap_95ci":ci,
            "attempted_group_summaries":group_summaries,"group_bootstrap_seed":seed,"group_bootstrap_replicates":n_boot,
            "note": "Group labels supplied by caller are not proof of experiment independence; the bootstrap interval reflects only resampling submitted group labels and cannot establish causal or cross-source validity."}
