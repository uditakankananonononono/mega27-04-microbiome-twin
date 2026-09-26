"""Fail-closed local intake for researcher-supplied abundance tables.

This is a schema/QC report, not a prediction endpoint or a rights validator.
Input remains on the caller's machine; no networking, account or data storage.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

from .platform_schema import validate_abundance_table


ALLOWED_UNITS = ('counts', 'relative_abundance', 'absolute_abundance')


def inspect_local_matrix(path, *, unit, source_id, processing_authorized=False, subject_map=None):
    """Inspect a samples-by-taxa TSV with unique `sample_id` first column.

    An affirmative flag is a researcher declaration, NOT proof of consent or
    a data-use right. No IDs or abundances are included in the returned JSON.
    """
    file = Path(path)
    if not file.is_file():
        raise ValueError('input file not found')
    if unit not in ALLOWED_UNITS:
        raise ValueError('unit must be counts, relative_abundance or absolute_abundance')
    if processing_authorized is not True:
        raise ValueError('researcher authorization declaration required; source-specific data rights must be checked separately')
    if not source_id or not str(source_id).strip():
        raise ValueError('source_id required for provenance')
    if file.stat().st_size > 50_000_000:
        raise ValueError('input exceeds the 50 MB local-intake limit')
    delimiter = ',' if file.name.endswith(('.csv', '.csv.gz')) else '\t'
    if file.name.endswith('.gz'):
        raise ValueError('compressed input not supported in local intake')
    import csv
    with file.open(newline='') as handle:
        headers = next(csv.reader(handle, delimiter=delimiter), [])
    if len(headers) != len(set(headers)):
        raise ValueError('duplicate taxon or sample_id header')
    table = pd.read_csv(file, sep=delimiter, dtype=str, keep_default_na=False)
    if table.empty or table.columns[0] != 'sample_id' or len(table.columns) < 2:
        raise ValueError('table needs sample_id first and at least one taxon')
    taxa = list(table.columns[1:])
    if 'subject_id' in taxa:
        raise ValueError('subject_id must be supplied in a separate subject map, not as a taxon')
    ids = table.sample_id.tolist()
    if any(not x.strip() for x in ids + taxa) or len(set(ids)) != len(ids) or len(set(taxa)) != len(taxa):
        raise ValueError('sample/taxon IDs must be unique and nonempty')
    if table.iloc[:,1:].eq('').any().any():
        raise ValueError('missing abundance entry')
    try:
        numeric = table.iloc[:,1:].apply(pd.to_numeric, errors='raise').to_numpy(dtype=float)
    except (ValueError, TypeError) as e:
        raise ValueError('non-numeric abundance entry') from e
    base = validate_abundance_table(taxa, ids, numeric, unit=unit, source_id=source_id,
                                    consent_for_processing=processing_authorized)
    if unit == 'counts' and (numeric != np.floor(numeric)).any():
        raise ValueError('counts must be integers')
    grouped = None
    if subject_map is not None:
        mfile = Path(subject_map)
        if not mfile.is_file() or mfile.stat().st_size > 50_000_000:
            raise ValueError('missing or oversized subject map')
        mapper = pd.read_csv(mfile, sep=',', dtype=str, keep_default_na=False)
        if list(mapper.columns) != ['sample_id','subject_id']:
            raise ValueError('subject map needs exactly sample_id,subject_id')
        if mapper.sample_id.duplicated().any() or set(mapper.sample_id) != set(ids) or not mapper.subject_id.map(str.strip).all():
            raise ValueError('subject map must have exactly one nonempty subject for each sample')
        grouped = int(mapper.subject_id.nunique())
    result = {**base, 'sha256': hashlib.sha256(file.read_bytes()).hexdigest(),
              'subject_map_sha256': hashlib.sha256(Path(subject_map).read_bytes()).hexdigest() if subject_map else None,
              'subject_groups': grouped, 'grouped_split_ready': grouped is not None and grouped > 1,
              'min_nonzero_taxa_per_sample': int((numeric > 0).sum(1).min()),
              'max_nonzero_taxa_per_sample': int((numeric > 0).sum(1).max()),
              'authorization_declaration': True,
              'prediction': None, 'external_validation': False,
              'note': 'Local schema/QC only. Caller declaration does not verify rights or consent. No access control, split audit, model, uncertainty or clinical conclusion.'}
    return result
