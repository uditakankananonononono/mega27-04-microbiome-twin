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
    return {"status": "paired_metadata_candidate" if len(sets) >= 2 and len(intersection) >= min_paired else "insufficient_paired_samples",
            "paired_samples": len(intersection), "paired_sample_ids": sorted(map(str, intersection)),
            "modality_counts": {name: len(ids) for name, ids in sets.items()},
            "note": "Exact IDs only; verify subject identity, batch and sample aliquot outside this function."}


ALIGN_FIELDS = ('source_family','subject_id','collection_time','aliquot_group')

def assess_strict_alignment(modality_records, *, min_paired=20):
    """Validate exact submitted provenance per common sample, without clinical claims.

    Requires a common ID and matching source/subject/time/aliquot labels across
    two or more modalities. Does not verify a physical aliquot or identity.
    """
    allowed={'16S','metagenomics','metabolomics','functional_pathways'}
    if not isinstance(modality_records,dict) or not set(modality_records)<=allowed or len(modality_records)<2:
        raise ValueError('at least two known modalities required')
    if type(min_paired) is not int or min_paired<1:
        raise ValueError('min_paired must be positive integer')
    by_modality={}
    for name,records in modality_records.items():
        if not isinstance(records,(list,tuple)) or not records:
            raise ValueError('nonempty modality records required')
        values={}
        for row in records:
            if not isinstance(row,dict) or any(key not in row or not isinstance(row[key],str) or not row[key].strip() or row[key]!=row[key].strip() for key in ('sample_id',*ALIGN_FIELDS)):
                raise ValueError('nonempty exact string provenance labels required')
            sample=row['sample_id']
            if sample in values:raise ValueError('duplicate sample ID in modality')
            values[sample]=tuple(row[key] for key in ALIGN_FIELDS)
        by_modality[name]=values
    common=set.intersection(*(set(rows) for rows in by_modality.values()))
    mismatched=[sid for sid in common if len({rows[sid] for rows in by_modality.values()})!=1]
    if mismatched:raise ValueError('cross-modality provenance conflict')
    return {'status':'metadata_aligned_candidate' if len(common)>=min_paired else 'insufficient_paired_samples',
            'modalities':len(by_modality),'modality_counts':{name:len(rows) for name,rows in by_modality.items()},
            'aligned_common_samples':len(common),
            'submitted_subject_groups':len({next(iter(by_modality.values()))[sid][:2] for sid in common}),
            'submitted_source_families':len({next(iter(by_modality.values()))[sid][0] for sid in common}),
            'submitted_collection_times':len({next(iter(by_modality.values()))[sid][2] for sid in common}),
            'physical_aliquot_verified':False,'biological_independence_verified':False,
            'note':'Exact submitted source/subject/time/aliquot labels agree, but labels alone cannot verify specimens, people, rights, assays or source-family independence.'}
