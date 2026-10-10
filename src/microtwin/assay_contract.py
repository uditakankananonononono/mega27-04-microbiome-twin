"""Explicit measurement contracts for cross-assay research inputs."""
from __future__ import annotations
import math
FIELDS=('source_family','material','assay','taxonomy_version','processing_pipeline','unit')

def assess_measurement_contract(train, query):
    """Describe comparability; never certify transfer from a matching label."""
    for label,record in [('train',train),('query',query)]:
        if not isinstance(record,dict):raise ValueError(f'{label} must be a contract object')
        for key in FIELDS:
            if not isinstance(record.get(key),str) or not record[key].strip():
                raise ValueError(f'{label}: {key} must be explicitly stated')
        if record['unit'] not in ('counts','relative_abundance','absolute_abundance'):
            raise ValueError(f'{label}: unsupported unit')
    mismatches=[key for key in FIELDS if train[key]!=query[key]]
    measurement_mismatches=[key for key in mismatches if key!='source_family']
    return {'measurement_fields_match':not measurement_mismatches,'mismatched_fields':mismatches,
            'independent_source_family_claimed':train['source_family']!=query['source_family'],
            'transfer_eligible':False,'individual_twin_eligible':False,
            'status':'needs_source_validation' if not measurement_mismatches else 'abstain_measurement_mismatch',
            'note':'Matching labels do not verify identities, rights, independence or external calibration. Different assays require a validated bridge; equal genus names do not establish equal measurements.'}


def parse_contract_json(raw, *, label="contract JSON"):
    """Reject ambiguous JSON instead of choosing a duplicate field silently."""
    import json
    def unique_object(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError('duplicate field')
            obj[key] = value
        return obj
    try:
        return json.loads(raw, object_pairs_hook=unique_object)
    except (ValueError, UnicodeError, TypeError, RecursionError) as exc:
        raise ValueError(f'{label} must be well-formed UTF-8 with unique fields') from exc
