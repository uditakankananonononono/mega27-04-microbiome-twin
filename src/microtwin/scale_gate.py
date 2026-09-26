"""Measured dataset scale, not projected foundation-model milestones."""
from __future__ import annotations


def scale_status(records, *, target_min=500, target_max=1000, foundation_min=1000,
                 foundation_samples=1_000_000):
    """Count only separately verified study accessions and measured samples.

    The counts are claim gates, not a dataset search or pretraining job.
    """
    if target_min < 1 or target_max < target_min or foundation_min < target_max:
        raise ValueError("invalid scale targets")
    rows=list(records)
    verified=[r for r in rows if r.get('independence_verified') is True and
              r.get('license_verified') is True and r.get('input_qc_passed') is True and
              r.get('source_hash_verified') is True]
    ids=[str(r.get('accession','')).strip() for r in verified]
    if any(not x for x in ids) or len(ids)!=len(set(ids)):
        raise ValueError("verified accessions must be nonempty and unique")
    samples=[]
    for r in verified:
        n=r.get('independent_samples')
        if not isinstance(n,int) or n<1:raise ValueError("sample count must be verified positive integer")
        samples.append(n)
    return {'manifest_rows':len(rows),'verified_datasets':len(verified),
            'verified_independent_samples':sum(samples),
            'leaderboard_scale_500_1000':target_min<=len(verified)<=target_max,
            'foundation_scale_target_met':len(verified)>=foundation_min and sum(samples)>=foundation_samples,
            'note':'Scale gate alone says nothing about model fit, multimodal pairs, quality or benchmark success.'}
