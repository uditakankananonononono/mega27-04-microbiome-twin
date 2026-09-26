"""Conservative lineage guard for documented cross-accession mirrors.

A passing result only excludes *known* source collisions; it never certifies
participant-level independence or final external-test eligibility.
"""
from __future__ import annotations

from collections import defaultdict


def check_family_partitions(records, known_families):
    """Fail closed when documented aliases bridge data partitions.

    known_families maps a canonical biological source to iterable accessions.
    Records require an accession, family membership and train/validation/test
    partition. Unknown accessions are not independent by default.
    """
    alias_to_family = {}
    for family, aliases in known_families.items():
        if not isinstance(family, str) or not family.strip() or isinstance(aliases, str):
            raise ValueError('invalid source family mapping')
        for alias in aliases:
            if not isinstance(alias, str) or not alias.strip():
                raise ValueError('blank source accession')
            alias = alias.strip().upper()
            prior = alias_to_family.get(alias)
            if prior is not None and prior != family:
                raise ValueError('accession belongs to conflicting source families')
            alias_to_family[alias] = family
    errors = []
    partitions = defaultdict(set)
    rows = list(records)
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append({'row': i, 'reason': 'invalid_record'})
            continue
        accession = str(row.get('accession') or '').strip().upper()
        partition = str(row.get('partition') or '').strip()
        if partition not in ('train', 'validation', 'test'):
            errors.append({'row': i, 'reason': 'invalid_partition'})
        if accession not in alias_to_family:
            errors.append({'row': i, 'reason': 'unknown_source_family'})
        elif partition in ('train', 'validation', 'test'):
            partitions[alias_to_family[accession]].add(partition)
    for family, parts in partitions.items():
        if len(parts) > 1:
            errors.append({'reason': 'cross_partition_family', 'family': family,
                           'partitions': sorted(parts)})
    return {'valid_known_family_separation_only': not errors,
            'records': len(rows), 'errors': errors,
            'note': 'Passing does not establish rights, source completeness, near-duplicate freedom or patient independence.'}
