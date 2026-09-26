"""Research-use input validation before creating an individual twin."""
from __future__ import annotations

import numpy as np


def validate_abundance_table(taxa, samples, values, *, unit, source_id, consent_for_processing=False):
    """Fail closed on invalid matrices and unsupported clinical use.

    IDs should be pseudonymous. Caller still must enforce access controls and
    source-specific permissions; this function does not grant data rights.
    """
    if unit not in ("counts", "relative_abundance", "absolute_abundance"):
        raise ValueError("unit must state counts, relative_abundance or absolute_abundance")
    if not source_id or not str(source_id).strip():
        raise ValueError("source_id required for provenance")
    if consent_for_processing is not True:
        raise ValueError("consent_for_processing must be confirmed for this dataset")
    taxa, samples = list(taxa), list(samples)
    if not taxa or not samples or len(set(taxa)) != len(taxa) or len(set(samples)) != len(samples):
        raise ValueError("nonempty unique taxa and sample IDs required")
    matrix = np.asarray(values)
    if matrix.shape != (len(samples), len(taxa)):
        raise ValueError("expected samples x taxa matrix")
    if not np.issubdtype(matrix.dtype, np.number) or not np.isfinite(matrix).all() or (matrix < 0).any():
        raise ValueError("finite nonnegative numeric values required")
    if (matrix.sum(1) <= 0).any():
        raise ValueError("zero-mass sample cannot be modeled")
    if unit == "relative_abundance" and not np.allclose(matrix.sum(1), 1, rtol=1e-4, atol=1e-4):
        raise ValueError("relative-abundance rows must sum to one")
    return {"samples": len(samples), "taxa": len(taxa), "unit": unit, "source_id": str(source_id),
            "status": "schema_validated_only", "note": "No model fit, privacy audit, subject independence or clinical validation implied."}
