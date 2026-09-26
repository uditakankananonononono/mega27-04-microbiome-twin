"""Source-specific subject grouping, never inferred from generic sample IDs."""
from __future__ import annotations

import re

_ORAL_ID = re.compile(r"^(PK\d+)([HD])$")


def oral_subject_map(sample_records):
    """MGYS00002146 only: group H/D sites by the PK numeric person prefix.

    Requires source-specific sample descriptions to support the pair. Do not
    apply this naming pattern to other studies without independent validation.
    """
    mapping = {}
    for rec in sample_records:
        a = rec.get("attributes", {})
        sid, name = rec.get("id"), a.get("sample-name")
        m = _ORAL_ID.fullmatch(str(name or ""))
        if not sid or not m or sid in mapping:
            raise ValueError("missing, duplicate or nonconforming oral sample ID")
        description = str(a.get("sample-desc") or "").lower()
        if m.group(2) == "D" and "diseased area of diseased individual" not in description:
            raise ValueError("diseased-site person linkage not verified by description")
        if m.group(2) == "H" and not ("healthy area of diseased individual" in description or
                                       "healthy individual" in description):
            raise ValueError("healthy-site subject description not verified")
        mapping[sid] = {"subject":m.group(1), "site":m.group(2), "sample_name":name}
    return {"samples":len(mapping),"subjects":len({v['subject'] for v in mapping.values()}),
            "mapping":mapping,"scope":"MGYS00002146 only, source-description-derived"}
