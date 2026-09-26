"""Create an outcome-blind EMP subset excluding ambiguous genus-lineage names.

The earlier `emp_2k_candidate_genus.tsv.gz` is an archived diagnostic and is
not silently rewritten. This output is a separate candidate for future work.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
from microtwin.emp_taxonomy import unambiguous_genus_mapping

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/source_family_candidates/EMP'
BIOM = BASE / 'emp_cr_gg_13_8.release1.biom'
EXPECTED_MD5 = '5a08ab0811582bbc8f87a923d5c90f73'
OUT = BASE / 'emp_2k_unambiguous_genus.tsv.gz'


def main():
    if hashlib.md5(BIOM.read_bytes()).hexdigest() != EXPECTED_MD5:
        raise ValueError('EMP BIOM checksum mismatch')
    meta = pd.read_csv(BASE / 'emp_mapping_subset_2k.tsv', sep='\t', low_memory=False)
    old = set(pd.read_csv(ROOT / 'data/raw/mgnify/manifest.csv').secondary_accession.dropna().astype(str))
    meta = meta[~meta.ebi_accession.astype(str).isin(old) & meta.host_subject_id.notna()]
    counts = meta.study_id.value_counts()
    meta = meta[meta.study_id.isin(counts[counts >= 20].index)]
    ids = meta['#SampleID'].astype(str).tolist()
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate metadata sample ID')
    with h5py.File(BIOM) as f:
        sample_ids = [v.decode() for v in f['sample']['ids'][:]]
        positions = {sid: i for i, sid in enumerate(sample_ids)}
        if not set(ids) <= set(positions):
            raise ValueError('sample ID absent from BIOM')
        labels, ambiguous = unambiguous_genus_mapping(f['observation']['metadata']['taxonomy'][:])
        genera = sorted(set(labels) - {None})
        lookup = {g: i for i, g in enumerate(genera)}
        feature_idx = np.array([lookup.get(g, -1) for g in labels], dtype=np.int32)
        mat = f['sample']['matrix']
        ptr, ind, val = mat['indptr'][:], mat['indices'][:], mat['data'][:]
        out = np.zeros((len(genera), len(ids)), dtype=np.float64)
        total = np.zeros(len(ids), dtype=np.float64)
        excluded = np.zeros(len(ids), dtype=np.float64)
        for j, sid in enumerate(ids):
            i = positions[sid]
            start, end = ptr[i:i+2]
            target = feature_idx[ind[start:end]]
            weights = val[start:end]
            good = target >= 0
            np.add.at(out[:, j], target[good], weights[good])
            total[j] = weights[good].sum()
            excluded[j] = weights[~good].sum()
    df = pd.DataFrame(out, index=genera, columns=ids)
    df.to_csv(OUT, sep='\t', compression='gzip')
    sample_audit = pd.DataFrame({'sample_id': ids, 'study_id': meta.study_id.to_numpy(),
                                 'retained_named_unambiguous_mass': total,
                                 'excluded_ambiguous_or_unnamed_mass': excluded})
    study_audit = {}
    for sid, group in sample_audit.groupby('study_id'):
        frac = group.retained_named_unambiguous_mass / (
            group.retained_named_unambiguous_mass + group.excluded_ambiguous_or_unnamed_mass)
        study_audit[str(int(sid))] = {'samples': len(group),
                                     'retained_raw_mass_median': float(frac.median()),
                                     'retained_raw_mass_minimum': float(frac.min())}
    info = {
        'source_biom_md5': EXPECTED_MD5,
        'source_url': 'https://zenodo.org/records/890000/files/emp_cr_gg_13_8.release1.biom?download=1',
        'genus_rows': len(genera), 'sample_columns': len(ids),
        'ambiguous_genus_names_excluded': sorted(ambiguous),
        'ambiguous_genus_name_count': len(ambiguous),
        'sample_retained_mass_median': float(np.median(total / (total + excluded))),
        'sample_retained_mass_minimum': float(np.min(total / (total + excluded))),
        'zero_retained_mass_samples': int((total == 0).sum()),
        'study_retained_mass': study_audit,
        'output_sha256': hashlib.sha256(OUT.read_bytes()).hexdigest(),
        'status': 'outcome_blind_taxonomy_candidate_not_benchmark',
        'note': 'Excludes all same-name conflicting parental lineages. Also excludes unnamed genera. Does not resolve taxonomy-version synonyms or prove source independence.'
    }
    (BASE / 'emp_2k_unambiguous_genus_info.json').write_text(json.dumps(info, indent=2) + '\n')
    print(json.dumps({k: v for k, v in info.items() if k != 'ambiguous_genus_names_excluded'}, indent=2))


if __name__ == '__main__':
    main()
