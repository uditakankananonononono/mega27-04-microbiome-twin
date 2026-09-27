"""Prospective keystone ranking evaluation under measured environmental change."""
from __future__ import annotations

import numpy as np


def prospective_precision_at_k(scores, measured_effect, groups, *, k=5, effect_cutoff=0):
    """Evaluate rank against independently measured post-perturbation effects.

    This is an evaluation primitive, not a definition that a network hub is a
    biological keystone. Labels must be declared before model training.
    """
    s=np.asarray(scores,float); y=np.asarray(measured_effect,float); g=list(groups)
    if s.ndim!=1 or s.shape!=y.shape or len(g)!=len(s) or not len(s):
        raise ValueError("aligned nonempty arrays required")
    if not np.isfinite(s).all() or not np.isfinite(y).all() or not np.isfinite(effect_cutoff) or effect_cutoff<0:
        raise ValueError("finite scores/effects and nonnegative cutoff required")
    if any(x is None or not str(x).strip() or
           (isinstance(x, (float, np.floating)) and not np.isfinite(x)) for x in g):
        raise ValueError("independent experiment group required")
    g=[str(x).strip() for x in g]
    if not isinstance(k,int) or isinstance(k,bool) or k<1:raise ValueError("k must be positive integer")
    out={}
    for group in dict.fromkeys(g):
        idx=np.flatnonzero(np.asarray(g,dtype=object)==group)
        top=idx[np.argsort(-s[idx],kind="stable")[:min(k,len(idx))]]
        out[str(group)]={"n_taxa":len(idx),"k":len(top),
                         "precision_at_k":float((np.abs(y[top])>effect_cutoff).mean())}
    return {"status":"measured_perturbation_labels_required", "per_experiment":out,
            "macro_precision_at_k":float(np.mean([v['precision_at_k'] for v in out.values()])),
            "n_experiments":len(out),
            "note":"Caller-supplied group labels are not proof of experiment independence. Positive label is externally measured change beyond locked cutoff; not inferred graph centrality."}
