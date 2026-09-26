"""MGnify taxonomy table source integrity checks, before modeling.

Analyses are not independent samples. Prefer direct run analyses when both a
run and a derived assembly represent the same biological sample.
"""
from __future__ import annotations

from collections import defaultdict


def select_run_columns(table_columns, analyses):
    """Map MGnify analysis records to table columns and unique sample IDs.

    `analyses` are API `data` records from all pages of the study analyses endpoint.
    Raise on ambiguous sample-to-run mapping or missing expected run columns.
    Do not infer independence of different samples/patients from this mapping.
    """
    by_sample = defaultdict(set)
    assembly_by_sample = defaultdict(set)
    columns = list(table_columns)
    if len(columns) != len(set(columns)):
        raise ValueError("duplicate table column IDs")
    colset = set(columns)
    if not analyses:
        raise ValueError("analyses must be supplied from all endpoint pages")
    for a in analyses:
        rel = a.get("relationships", {})
        sid = (rel.get("sample") or {}).get("data") or {}
        sid = sid.get("id")
        if not sid:
            raise ValueError("analysis missing sample ID")
        run = (rel.get("run") or {}).get("data") or {}
        asm = (rel.get("assembly") or {}).get("data") or {}
        if run.get("id"):
            by_sample[sid].add(run["id"])
        if asm.get("id"):
            assembly_by_sample[sid].add(asm["id"])
    ambiguous = {sample: sorted(runs) for sample, runs in by_sample.items() if len(runs) != 1}
    if ambiguous:
        raise ValueError(f"ambiguous or missing run IDs for {len(ambiguous)} samples")
    selected = {next(iter(runs)) for runs in by_sample.values()}
    missing = sorted(selected - colset)
    if missing:
        raise ValueError(f"run columns missing from downloaded table: {missing[:5]}")
    if len(selected) != len(by_sample):
        raise ValueError("multiple sample IDs map to the same run ID")
    excluded = sorted(colset - selected)
    unexplained = set(excluded) - set().union(*assembly_by_sample.values())
    if unexplained:
        raise ValueError(f"unexplained non-run columns: {sorted(unexplained)[:5]}")
    return {"sample_count": len(by_sample), "selected_run_columns": [c for c in columns if c in selected],
            "excluded_assembly_columns": excluded,
            "samples_with_assembly": sum(bool(x) for x in assembly_by_sample.values()),
            "note": "Only analysis-to-sample identity checked; patients, modality and cross-study duplicates unverified."}
