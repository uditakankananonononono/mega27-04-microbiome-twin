"""Check paired-sample alignment for multimodal microbiome comparisons."""
from __future__ import annotations


def assess_modalities(modality_samples, *, min_paired=20):
    """Report the intersection; unrelated cohorts cannot be joined by row order."""
    allowed = {"16S", "metagenomics", "metabolomics", "functional_pathways"}
    if not isinstance(modality_samples, dict) or set(modality_samples) - allowed:
        raise ValueError("unknown modality")
    if not isinstance(min_paired, int) or isinstance(min_paired, bool) or min_paired < 1:
        raise ValueError("min_paired must be positive integer")
    sets = {}
    for modality, ids in modality_samples.items():
        sample_ids = list(ids)
        if any(i is None or not str(i).strip() for i in sample_ids):
            raise ValueError("sample IDs must be nonblank and unique within each modality")
        normalized = [str(i).strip() for i in sample_ids]
        if len(set(normalized)) != len(normalized):
            raise ValueError("sample IDs must be nonblank and unique within each modality")
        sets[modality] = set(normalized)
    if not sets:
        return {"status": "unavailable_no_modalities", "paired_samples": 0,
                "paired_sample_ids": [], "modality_counts": {}}
    intersection = set.intersection(*sets.values())
    return {"status": "paired_metadata_candidate" if len(intersection) >= min_paired else "insufficient_paired_samples",
            "paired_samples": len(intersection), "paired_sample_ids": sorted(map(str, intersection)),
            "modality_counts": {name: len(ids) for name, ids in sets.items()},
            "note": "Exact IDs only; verify subject identity, batch and sample aliquot outside this function."}
