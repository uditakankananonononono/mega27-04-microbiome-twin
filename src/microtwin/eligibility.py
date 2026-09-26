"""Conservative source-manifest checks before any cross-study leaderboard.

This validates metadata only. It never calls an accession an independent eligible
cohort just because a row exists in a manifest.
"""
from __future__ import annotations

import re
from collections import Counter

ASSEMBLY = re.compile(r"\b(?:metagenome assembly|tpa metagenomics assembly|assembly of)\b", re.I)


def assess_records(records):
    """Classify study records and surface potential duplicates for manual review.

    Expected keys: study, secondary_accession, biome, n_samples, n_genera,
    file, source_url, study_name. No file is counted as verified without checking
    its bytes and modality outside this function.
    """
    rows = [dict(row) for row in records]
    studies = Counter(str(r.get("study", "")).strip() for r in rows)
    secondary = Counter(str(r.get("secondary_accession", "")).strip() for r in rows)
    out = []
    for r in rows:
        reasons = []
        sid = str(r.get("study", "")).strip()
        accession = str(r.get("secondary_accession", "")).strip()
        if not sid or sid.lower() == "nan" or studies[sid] > 1:
            reasons.append("missing_or_duplicate_study_id")
        if not accession or accession.lower() == "nan" or secondary[accession] > 1:
            reasons.append("missing_or_duplicate_secondary_accession")
        if ASSEMBLY.search(str(r.get("study_name", ""))):
            reasons.append("possible_assembly_not_independent_biological_cohort")
        try:
            n_samples = int(r.get("n_samples", 0))
            n_genera = int(r.get("n_genera", 0))
        except (TypeError, ValueError):
            n_samples = n_genera = 0
        if n_samples < 20 or n_genera < 10:
            reasons.append("insufficient_manifest_dimensions")
        if not str(r.get("source_url", "")).startswith("https://www.ebi.ac.uk/metagenomics/"):
            reasons.append("source_url_unverified")
        if not str(r.get("file", "")).strip():
            reasons.append("missing_local_file_path")
        out.append({"study": sid, "secondary_accession": accession,
                    "biome": str(r.get("biome", "")), "manifest_samples": n_samples,
                    "status": "metadata_candidate" if not reasons else "review_required",
                    "reasons": reasons})
    return {"manifest_rows": len(rows), "unique_study_ids": len(set(studies) - {""}),
            "metadata_candidates": sum(r["status"] == "metadata_candidate" for r in out),
            "review_required": sum(r["status"] == "review_required" for r in out),
            "verified_independent_datasets": 0,
            "note": "Metadata screening only: underlying file bytes, overlap, modality, license, subject identity and external-study eligibility remain unverified.",
            "records": out}
