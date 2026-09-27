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
    if not isinstance(known_families, dict):
        raise ValueError('source family mapping must be a dictionary')
    alias_to_family = {}
    for family, aliases in known_families.items():
        if not isinstance(family, str) or not family.strip() or isinstance(aliases, str):
            raise ValueError('invalid source family mapping')
        try:
            aliases = list(aliases)
        except TypeError as exc:
            raise ValueError('invalid source family mapping') from exc
        if not aliases:
            raise ValueError('source family mapping requires aliases')
        for alias in aliases:
            if not isinstance(alias, str) or not alias.strip():
                raise ValueError('blank source accession')
            alias = alias.strip().upper()
            if alias in alias_to_family:
                if alias_to_family[alias] != family:
                    raise ValueError('accession belongs to conflicting source families')
                raise ValueError('duplicate accession in source family mapping')
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


def known_mgnify_original_project_families():
    """Return source-confirmed aliases for an original project behind two MGnify assemblies.

    This is deliberately a small positive registry, not a complete family map.
    A caller must merge it with its own verified aliases and still fail closed
    on unknowns; shared project provenance is not duplicate-sample evidence.
    """
    return {'PRJNA715245': ('PRJNA715245', 'MGYS00006825', 'ERP160132',
                            'PRJEB75554', 'MGYS00006862', 'ERP175206',
                            'PRJEB92327')}
