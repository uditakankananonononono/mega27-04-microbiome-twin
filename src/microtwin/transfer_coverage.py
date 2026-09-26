"""Outcome-blind vocabulary overlap checks for cross-source transfer."""
from __future__ import annotations

import numpy as np
import pandas as pd


def vocabulary_coverage(train_genus, test_counts):
    """Measure test mass retained by train taxa before any outcome scoring.

    Reports whether a fixed vocabulary can be used, not whether it predicts.
    Study-level selection and taxonomy synonym mapping remain separate.
    """
    names = set(train_genus)
    if not names or not isinstance(test_counts, pd.DataFrame) or test_counts.empty:
        raise ValueError("nonempty train vocabulary and test count matrix required")
    if not test_counts.index.is_unique or not test_counts.columns.is_unique:
        raise ValueError("test genus and sample IDs must be unique")
    x = test_counts.to_numpy()
    if not np.issubdtype(x.dtype,np.number) or not np.isfinite(x).all() or (x<0).any():
        raise ValueError("finite nonnegative test counts required")
    total = test_counts.sum(0)
    if (total<=0).any():raise ValueError("zero-mass test sample")
    overlap = names & set(test_counts.index)
    retained = test_counts.loc[sorted(overlap)].sum(0)/total
    return {"train_genera":len(names),"test_genera":len(test_counts),"shared_genera":len(overlap),
            "test_samples":len(total),"median_test_mass_covered":float(retained.median()),
            "minimum_test_mass_covered":float(retained.min()),
            "note":"Counts-only coverage: no outcomes, prediction fit, synonym harmonization or source-independence proof."}
