"""Outcome-blind input-vocabulary QC for HMP V1-3 against old MGnify oral pilot.

Never fits a model or scores abundance predictions. These inputs are now
viewed for method development and cannot be future untouched final holdouts.
"""
from __future__ import annotations

import csv
import gzip
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from microtwin.genus_harmonize import terminal_genus
from microtwin.coverage_gate import coverage_gate
from hmp_v13_intake import EXPECTED, SOURCE, lineage
import hashlib

ROOT = Path(__file__).resolve().parents[1]


def main():
    for filename, expected in EXPECTED.items():
        if hashlib.sha256((SOURCE / filename).read_bytes()).hexdigest() != expected:
            raise ValueError(f'{filename}: SHA256 mismatch')
    train, _ = terminal_genus(pd.read_csv(ROOT / 'data/pilot_external/MGYS00002394_raw.tsv', sep='\t', index_col=0))
    vocabulary = set(train.index)
    metadata = pd.read_csv(SOURCE / 'v13_map_uniquebyPSN.txt.bz2', sep='\t', dtype={'#SampleID':str,'RSID':str})
    if metadata['#SampleID'].duplicated().any(): raise ValueError('duplicate metadata sample')
    with gzip.open(SOURCE / 'otu_table_psn_v13.txt.gz', 'rt', newline='') as handle:
        handle.readline(); reader=csv.reader(handle,delimiter='\t');fields=next(reader)
        ids = fields[1:-1]
        parents=defaultdict(set)
        for row in reader:
            if len(row)!=len(fields):raise ValueError('ragged OTU row')
            g,parent=lineage(row[-1])
            if g:parents[g].add(parent)
        ambiguous={g for g,paths in parents.items() if len(paths)>1}
    meta=metadata[metadata['#SampleID'].isin(ids)].set_index('#SampleID')
    positions=[i for i,sid in enumerate(ids) if sid in meta.index]
    joined_ids=[ids[i] for i in positions]
    if len(joined_ids)!=len(meta):raise ValueError('invalid sample join')
    mass=np.zeros(len(joined_ids),dtype=np.float64)
    valid=np.zeros(len(joined_ids),dtype=np.float64)
    compatible=np.zeros(len(joined_ids),dtype=np.float64)
    observed_named=set()
    with gzip.open(SOURCE / 'otu_table_psn_v13.txt.gz','rt',newline='') as handle:
        handle.readline();reader=csv.reader(handle,delimiter='\t');next(reader)
        for row in reader:
            counts=np.asarray([float(row[i+1]) for i in positions])
            if not np.isfinite(counts).all() or (counts<0).any():raise ValueError('invalid counts')
            mass+=counts
            genus,_=lineage(row[-1])
            if genus and genus not in ambiguous:
                valid+=counts
                if genus in vocabulary:
                    compatible+=counts
                    observed_named.add(genus)
    if (mass<=0).any():raise ValueError('zero raw mass')
    joined=meta.loc[joined_ids]
    rows=[]
    for site,group in joined.groupby('HMPbodysubsite'):
        positions=np.flatnonzero(joined.HMPbodysubsite.to_numpy()==site)
        x=compatible[positions]/mass[positions]
        y=valid[positions]/mass[positions]
        z=np.divide(compatible[positions],valid[positions],out=np.zeros(len(positions)),where=valid[positions]>0)
        # Default gate is applied to raw community mass; projected target alone
        # can hide loss of unnamed and taxonomy-ambiguous taxa.
        decision=coverage_gate({'shared_genera':len(observed_named),'minimum_test_mass_covered':float(x.min())})
        rows.append({'subsite':str(site),'samples':len(group),'people':int(group.RSID.nunique()),
                     'minimum_raw_mass_in_train_vocab':float(x.min()),
                     'median_raw_mass_in_train_vocab':float(np.median(x)),
                     'median_raw_mass_named_unambiguous':float(np.median(y)),
                     'median_named_unambiguous_mass_in_train_vocab':float(np.median(z)),
                     'input_vocabulary_gate':decision['eligible_on_vocabulary_only'],
                     'gate_reasons':decision['reasons']})
    out={'status':'input_only_coverage_diagnostic_not_external_score',
         'train_source':'MGYS00002394','train_genera':len(vocabulary),
         'shared_unambiguous_hmp_genera_seen':len(observed_named),
         'hmp_source_commit':'a9807c3ed97f24c94d40fc4e62329a2d83a7e673',
         'mapped_samples':len(joined_ids),'subsites':rows,
         'note':'No model fit or test errors. Every HMP subsite was inspected for input QC, so HMP is now development diagnostic, not untouched final holdout. Even an input gate pass would not prove source independence, rights, assay compatibility or useful prediction.'}
    (ROOT/'results/hmp_v13_input_coverage.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'shared':len(observed_named),'pass_subsites':[r['subsite'] for r in rows if r['input_vocabulary_gate']],
                      'subsites':[{k:r[k] for k in ('subsite','samples','minimum_raw_mass_in_train_vocab','median_raw_mass_in_train_vocab')} for r in rows]},indent=2))

if __name__=='__main__':main()
