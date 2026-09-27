"""Measured dataset scale, not projected foundation-model milestones."""
from __future__ import annotations


def scale_status(records, *, target_min=500, target_max=1000, foundation_min=1000,
                 foundation_samples=1_000_000):
    """Count only separately verified study accessions and measured samples.

    The counts are claim gates, not a dataset search or pretraining job.
    """
    targets = (target_min, target_max, foundation_min, foundation_samples)
    if any(not isinstance(n, int) or isinstance(n, bool) for n in targets):
        raise ValueError("scale targets must be integer counts")
    if foundation_samples < 1 or target_min < 1 or target_max < target_min or foundation_min < target_max:
        raise ValueError("invalid scale targets")
    rows=list(records)
    if any(not isinstance(r, dict) for r in rows):
        raise ValueError("scale records must be mappings")
    verified=[r for r in rows if r.get('independence_verified') is True and
              r.get('license_verified') is True and r.get('input_qc_passed') is True and
              r.get('source_hash_verified') is True]
    ids=[str(r.get('accession','')).strip().upper() for r in verified]
    if any(not x for x in ids) or len(ids)!=len(set(ids)):
        raise ValueError("verified accessions must be nonempty and unique")
    families=[str(r.get('source_family') or '').strip().upper() for r in verified]
    if any(not family for family in families):
        raise ValueError('verified source_family required for each counted accession')
    if len(families)!=len(set(families)):
        raise ValueError('verified biological source families must be unique across accessions')
    samples=[]
    for r in verified:
        n=r.get('independent_samples')
        if not isinstance(n,int) or isinstance(n,bool) or n<1:
            raise ValueError("sample count must be verified positive integer")
        samples.append(n)
    return {'manifest_rows':len(rows),'verified_datasets':len(verified),'verified_biological_families':len(families),
            'verified_independent_samples':sum(samples),
            'leaderboard_scale_500_1000':target_min<=len(verified)<=target_max,
            'foundation_scale_target_met':len(verified)>=foundation_min and sum(samples)>=foundation_samples,
            'note':'Caller-supplied source-family labels and flags do not independently prove lineage or rights. Scale gate alone says nothing about model fit, multimodal pairs, quality or benchmark success.'}
