"""Local, conservative composition prediction from an assemblage.

This is the presence-conditional population prior, not an intervention model or
an individual clinical twin. It neither exports data nor estimates uncertainty.
"""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

from .research_intake import inspect_local_matrix


def _read_table(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size > 50_000_000 or path.suffix not in ('.csv', '.tsv'):
        raise ValueError('missing, oversized or unsupported local table (CSV/TSV, 50 MB maximum)')
    delimiter = ',' if path.suffix == '.csv' else '\t'
    with path.open(newline='') as f:
        hdr = next(csv.reader(f, delimiter=delimiter), [])
    if len(hdr) != len(set(hdr)) or len(hdr) < 2 or hdr[0] != 'sample_id' or any(not x.strip() for x in hdr):
        raise ValueError('sample_id first, then unique nonempty taxon names required')
    df = pd.read_csv(path, sep=delimiter, dtype=str, keep_default_na=False)
    if df.empty or df.sample_id.map(str.strip).eq('').any() or df.sample_id.duplicated().any():
        raise ValueError('nonempty unique sample IDs required')
    if df.iloc[:, 1:].eq('').any().any():
        raise ValueError('missing value in local table')
    try:
        vals = df.iloc[:, 1:].apply(pd.to_numeric, errors='raise').to_numpy(dtype=float)
    except (ValueError, TypeError) as e:
        raise ValueError('numeric entries required') from e
    if not np.isfinite(vals).all():
        raise ValueError('finite entries required')
    return df.sample_id.tolist(), hdr[1:], vals, hashlib.sha256(path.read_bytes()).hexdigest()


def predict_local(train_path, query_path, *, unit, source_id, processing_authorized=False, subject_map=None):
    """Return predictions (query sample x taxon) and a non-clinical provenance report.

    No fit or selection uses query abundances: queries are strictly binary
    assemblages. Exact taxon-name alignment and known training vocabulary are
    required; a different assay or taxonomy needs separate validation.
    """
    qc = inspect_local_matrix(train_path, unit=unit, source_id=source_id,
                              processing_authorized=processing_authorized, subject_map=subject_map)
    train_ids, taxa, x, train_sha = _read_table(train_path)
    if unit == 'counts' and (x != np.floor(x)).any():
        raise ValueError('counts must be integers')
    if unit == 'relative_abundance' and not np.allclose(x.sum(axis=1), 1, atol=1e-4, rtol=1e-4):
        raise ValueError('relative abundance rows must sum to one')
    query_ids, qtaxa, z, query_sha = _read_table(query_path)
    if train_sha != qc['sha256']:
        raise ValueError('training file changed during inspection')
    if qtaxa != taxa:
        raise ValueError('query taxa and order must match training table exactly; taxonomy translation is not automatic')
    if set(train_ids) & set(query_ids):
        raise ValueError('query sample ID overlaps training data')
    if not np.isin(z, [0, 1]).all() or (z.sum(axis=1) < 1).any():
        raise ValueError('query must be nonempty binary presence (0/1), not measured outcome abundances')
    x = x / x.sum(axis=1, keepdims=True)
    empirical_mean = x.mean(axis=0)
    # A taxon absent in all training samples has no estimated abundance; do not
    # assign it an invented weight or renormalize a wholly uncovered query.
    if (z[:, empirical_mean <= 0] > 0).any():
        raise ValueError('query contains present taxa absent from training; abstaining')
    # Match the published local PresenceMean implementation exactly after the
    # abstention check; smoothing never manufactures an unseen-present taxon.
    mean = empirical_mean + 1e-9
    mass = z @ mean
    if (mass <= 0).any():
        raise ValueError('at least one query has no taxon with positive training abundance; abstaining')
    pred = z * mean / mass[:, None]
    if hashlib.sha256(Path(train_path).read_bytes()).hexdigest() != train_sha:
        raise ValueError('training file changed during prediction')
    if hashlib.sha256(Path(query_path).read_bytes()).hexdigest() != query_sha:
        raise ValueError('query file changed during prediction')
    if subject_map is not None and hashlib.sha256(Path(subject_map).read_bytes()).hexdigest() != qc['subject_map_sha256']:
        raise ValueError('subject map changed during prediction')
    result = pd.DataFrame(pred, columns=taxa)
    result.insert(0, 'sample_id', query_ids)
    report = {'status': 'research_baseline_prediction', 'model': 'presence_conditional_population_mean',
              'source_id': source_id, 'train_sha256': train_sha, 'query_sha256': query_sha,
              'train_samples': len(train_ids), 'query_samples': len(query_ids), 'taxa': len(taxa),
              'subject_groups': qc['subject_groups'],
              'query_min_known_taxon_fraction': float(np.min(((z > 0) & (empirical_mean > 0)).sum(axis=1) / z.sum(axis=1))),
              'uncertainty': None, 'external_validation': False,
              'note': 'Local assemblage-to-composition population baseline only. Same taxon labels do not prove assay compatibility. No clinical, intervention, calibration or cross-source claim.'}
    return result, report
