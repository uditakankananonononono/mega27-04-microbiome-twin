"""Outcome-blind source/QC intake of public HMP V1-3 OTUs and subject map.

Inputs are the fixed files identified in data/source_family_candidates/HMP/README.md;
this is not an external model test, prediction, or permission check.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/source_family_candidates/HMP'
OUT = ROOT / 'results/hmp_v13_intake.json'
EXPECTED = {
    'otu_table_psn_v13.txt.gz': '876a4a5895995e89413b08ad9e53529c496df27134dcb344882605ba854fa272',
    'v13_map_uniquebyPSN.txt.bz2': '0659e84079cbcf900cf5b13841e460007b82e6d35bb5305f993e241d1118f805',
    'ppAll_V13_map.txt': '0618ca1771f8990a406479300accbaf4457405082a713e576e688089819e6f6a',
}

def lineage(row):
    parts = tuple(x.strip() for x in row.split(';'))
    genus = [x.removeprefix('g__').strip() for x in parts if x.startswith('g__')]
    if not genus or not genus[0] or genus[0].lower() in ('uncultured', 'unclassified'):
        return None, None
    return genus[0], parts[:-1]


def main():
    for filename, sha in EXPECTED.items():
        source = SOURCE / filename
        if hashlib.sha256(source.read_bytes()).hexdigest() != sha:
            raise ValueError(f'{filename}: source SHA256 mismatch')
    with gzip.open(SOURCE / 'otu_table_psn_v13.txt.gz', 'rt', newline='') as handle:
        handle.readline()  # QIIME comment
        reader = csv.reader(handle, delimiter='\t')
        fields = next(reader)
        sample_ids = fields[1:-1]
        if fields[0] != '#OTU ID' or fields[-1] != 'Consensus Lineage' or len(sample_ids) != len(set(sample_ids)):
            raise ValueError('unexpected OTU header or duplicate sample IDs')
        parent_paths = defaultdict(set)
        otus, unnamed = 0, 0
        for row in reader:
            if len(row) != len(fields): raise ValueError('ragged OTU table')
            genus, parent = lineage(row[-1])
            if genus is None: unnamed += 1
            else: parent_paths[genus].add(parent)
            otus += 1
        ambiguous = sorted(g for g, parents in parent_paths.items() if len(parents) > 1)
    metadata = pd.read_csv(SOURCE / 'v13_map_uniquebyPSN.txt.bz2', sep='\t', dtype={'#SampleID':str,'RSID':str})
    if metadata['#SampleID'].duplicated().any():raise ValueError('duplicate metadata sample ID')
    mapped = metadata[metadata['#SampleID'].isin(sample_ids)]
    if len(mapped) == 0 or mapped.RSID.isna().any():raise ValueError('no samples or missing subject IDs')
    mapped_by_id = mapped.set_index('#SampleID')
    idx = [i for i,sid in enumerate(sample_ids) if sid in mapped_by_id.index]
    valid_ids = [sample_ids[i] for i in idx]
    if len(valid_ids) != len(mapped):raise ValueError('matrix-map join failed')
    total = np.zeros(len(idx),dtype=np.float64)
    retained = np.zeros(len(idx),dtype=np.float64)
    genus_count = Counter()
    with gzip.open(SOURCE / 'otu_table_psn_v13.txt.gz', 'rt', newline='') as handle:
        handle.readline()
        reader = csv.reader(handle, delimiter='\t');next(reader)
        for row in reader:
            values = np.asarray([float(row[1+i]) for i in idx],dtype=np.float64)
            if not np.isfinite(values).all() or (values < 0).any():raise ValueError('invalid OTU counts')
            total += values
            genus, _ = lineage(row[-1])
            if genus and genus not in ambiguous:
                retained += values
                genus_count[genus] += 1
    if (total <= 0).any():raise ValueError('zero-raw-mass sample')
    fraction = retained/total
    old = pd.read_csv(ROOT / 'data/raw/mgnify/manifest.csv')
    manifest_text = old.astype(str).agg(' '.join,axis=1)
    matches = {token: int(manifest_text.str.contains(token,case=False,regex=False).sum())
               for token in ('SRP002395','SRP002012','HMP','Human Microbiome Project')}
    summary = {'status':'source_intake_only_not_external_benchmark',
        'source_commit':'a9807c3ed97f24c94d40fc4e62329a2d83a7e673',
        'sha256':EXPECTED, 'otu_rows':otus, 'matrix_sample_columns':len(sample_ids),
        'mapped_sample_columns':len(idx), 'unmapped_matrix_sample_columns':len(sample_ids)-len(idx),
        'mapped_distinct_subjects':int(mapped.RSID.nunique()),
        'mapped_distinct_subsites':int(mapped.HMPbodysubsite.nunique()),
        'mapped_visits':{str(k):int(v) for k,v in mapped.visitno.value_counts().items()},
        'mapped_subsite_sample_counts':{str(k):int(v) for k,v in mapped.HMPbodysubsite.value_counts().items()},
        'otu_rows_unnamed_genus':unnamed, 'genus_names_unique_after_ambiguity_exclusion':len(genus_count),
        'ambiguous_genus_names_excluded':ambiguous,
        'raw_mass_retained_named_unambiguous_median':float(np.median(fraction)),
        'raw_mass_retained_named_unambiguous_minimum':float(np.min(fraction)),
        'raw_mass_retained_named_unambiguous_stool_median':float(np.median(fraction[[valid_ids.index(sid) for sid in mapped[mapped.HMPbodysubsite=='Stool']['#SampleID']]])),
        'old_mgnify_manifest_textual_matches':matches,
        'note':'One HMP V1-3 source cohort, not 18 independent datasets. Multiple body sites and visits repeat people; zero textual overlap is not proof against sample mirroring. Raw source has public restricted metadata only; license/consent and taxonomy reference crosswalk remain to be verified. No model fit or outcome scoring.'}
    OUT.write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('sha256','mapped_subsite_sample_counts')},indent=2))

if __name__ == '__main__':main()
