"""Prevent source-family mirrors being counted as independent datasets."""
from __future__ import annotations


def validate_external_accessions(candidate_records, old_accessions):
    """Exclude exact EBI accessions and reject unverifiable identifiers.

    This does not detect study renames, republished samples or sequence overlap;
    no candidate passes final independence from this function alone.
    """
    old={str(x).strip() for x in old_accessions if str(x).strip()}
    out=[]
    for row in candidate_records:
        accession=str(row.get('ebi_accession') or '').strip()
        sid=str(row.get('study_id') or '').strip()
        if not accession or not sid:
            status='unverifiable_missing_accession_or_study'
        elif accession in old:
            status='excluded_exact_mirror'
        else:
            status='candidate_only_near_duplicate_unchecked'
        out.append({'study_id':sid,'ebi_accession':accession,'status':status})
    return {'total':len(out), 'excluded_exact_mirror':sum(r['status']=='excluded_exact_mirror' for r in out),
            'independence_verified':0,'records':out,
            'note':'Exact accession exclusion is necessary but insufficient for independent-source validation.'}
