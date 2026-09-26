"""Leakage guard for source/study/subject splits of microbiome records."""
from __future__ import annotations

from collections import defaultdict


def validate_disjoint(records, *, partition="partition", source="source",
                      study="study", subject="subject", fingerprint="fingerprint"):
    """Check nesting and exact-key collisions across partitions.

    A blank key is unknown rather than safe. An exact fingerprint only detects
    identical records, not sequence-level near duplicates or shared patients.
    """
    rows = [dict(r) for r in records]
    errs = []
    seen = {k: defaultdict(set) for k in (source, study, subject, fingerprint)}
    for i, r in enumerate(rows):
        part = str(r.get(partition) or "").strip()
        if part not in ("train", "validation", "test"):
            errs.append({"row": i, "reason": "missing_or_invalid_partition"})
            continue
        for col in (source, study):
            value = str(r.get(col) or "").strip()
            if not value:
                errs.append({"row": i, "reason": f"missing_{col}"})
            else:
                seen[col][value].add(part)
        for col in (subject, fingerprint):
            value = str(r.get(col) or "").strip()
            if value:
                seen[col][value].add(part)
    for col, values in seen.items():
        for value, parts in values.items():
            if len(parts) > 1:
                errs.append({"reason": f"cross_partition_{col}", "value": value,
                             "partitions": sorted(parts)})
    return {"valid": not errs, "rows": len(rows), "errors": errs,
            "limitations": ["Exact IDs/fingerprints cannot detect undocumented patient overlap or near-duplicate study data.",
                            "Source-level holdout requires trustworthy source labels and direct dataset verification."]}
