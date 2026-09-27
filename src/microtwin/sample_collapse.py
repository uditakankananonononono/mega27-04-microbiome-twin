"""Outcome-blind microbiome run/assembly harmonization.

MGnify SSU abundance matrices are taxa x analysis columns. Repeated runs for
one biological sample must be pooled before model fitting or splitting.
"""
from __future__ import annotations

from collections import defaultdict
import numpy as np
import pandas as pd


def collapse_runs(table, analyses):
    """Sum nonnegative raw abundance counts across runs of each sample.

    Assembly columns are excluded. This policy is valid only for compatible
    raw count tables for the same assay/pipeline; caller must verify those
    facts and independence/consent outside this function. It does not turn
    pooled sequencing runs into independent subjects.
    """
    if not isinstance(table, pd.DataFrame) or table.empty or not table.columns.is_unique:
        raise ValueError("nonempty table with unique analysis columns required")
    if not table.index.is_unique or any(not isinstance(v, str) or not v.strip() for v in table.index):
        raise ValueError("taxon rows must be unique nonempty labels before aggregation")
    if any(not isinstance(v, str) or not v.strip() for v in table.columns):
        raise ValueError("analysis columns must be nonempty string labels")
    vals = table.to_numpy()
    if not np.issubdtype(vals.dtype, np.number) or not np.isfinite(vals).all() or (vals < 0).any():
        raise ValueError("abundances must be finite nonnegative numeric values")
    if not analyses:
        raise ValueError("all analysis relationship records required")
    runs = defaultdict(set)
    assembly_ids = set()
    for a in analyses:
        if not isinstance(a, dict) or not isinstance(a.get("relationships"), dict):
            raise ValueError("each analysis needs relationship records")
        rel = a["relationships"]
        s = (rel.get("sample") or {}).get("data") or {}
        r = (rel.get("run") or {}).get("data") or {}
        asm = (rel.get("assembly") or {}).get("data") or {}
        if not isinstance(s.get("id"), str) or not s["id"].strip():
            raise ValueError("analysis without sample")
        if any(v.get("id") is not None and
               (not isinstance(v["id"], str) or not v["id"].strip()) for v in (r, asm)):
            raise ValueError("run or assembly id must be nonempty string")
        if r.get("id"):
            runs[s["id"]].add(r["id"])
        if asm.get("id"):
            assembly_ids.add(asm["id"])
    all_samples = {((a.get("relationships") or {}).get("sample") or {}).get("data", {}).get("id") for a in analyses}
    if all_samples - set(runs):
        raise ValueError("sample without a run")
    reverse = defaultdict(set)
    for sample, ids in runs.items():
        for rid in ids: reverse[rid].add(sample)
    if any(len(s) > 1 for s in reverse.values()):
        raise ValueError("run maps to multiple samples")
    if set(reverse) & assembly_ids:
        raise ValueError("run and assembly IDs collide; cannot identify raw counts")
    known = set(reverse) | assembly_ids
    extra = set(table.columns) - known
    missing = set(reverse) - set(table.columns)
    if extra or missing:
        raise ValueError(f"unexplained table columns: {len(extra)}; missing run columns: {len(missing)}")
    # Input taxonomy rows may include multiple ranks; caller handles genus
    # selection separately. Pool counts before composition normalization.
    out = pd.DataFrame({sample: table[list(ids)].sum(axis=1) for sample, ids in sorted(runs.items())})
    return out, {"samples": len(runs), "run_columns": len(reverse),
                 "excluded_assembly_columns": len(set(table.columns) & assembly_ids),
                 "multiple_run_samples": sum(len(x) > 1 for x in runs.values()),
                 "assumption": "sum compatible raw count runs before normalization; not independent subjects"}
