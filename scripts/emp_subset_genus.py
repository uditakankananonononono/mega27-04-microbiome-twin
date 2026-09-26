"""Extract frozen EMP 2k metadata-subset genus counts, no model outcomes."""
from __future__ import annotations
import hashlib,json
from collections import defaultdict
from pathlib import Path
import h5py,numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
BIOM=ROOT/'data/source_family_candidates/EMP/emp_cr_gg_13_8.release1.biom'
MAP=ROOT/'data/source_family_candidates/EMP/emp_mapping_subset_2k.tsv'
OLD=ROOT/'data/raw/mgnify/manifest.csv'
OUT=ROOT/'data/source_family_candidates/EMP/emp_2k_candidate_genus.tsv.gz'

def main():
    with h5py.File(BIOM) as f:
        ids=[v.decode() for v in f['sample']['ids'][:]]
        id_to_pos={name:i for i,name in enumerate(ids)}
        tax=f['observation']['metadata']['taxonomy'][:]
        names=[row[5].decode().removeprefix('g__') for row in tax]
        mat=f['sample']['matrix']
        indptr=mat['indptr'][:]
        indices=mat['indices'][:]
        values=mat['data'][:]
    meta=pd.read_csv(MAP,sep='\t',low_memory=False)
    old=set(pd.read_csv(OLD).secondary_accession.dropna().astype(str))
    meta=meta[~meta.ebi_accession.astype(str).isin(old) & meta.host_subject_id.notna()]
    counts=meta.study_id.value_counts()
    meta=meta[meta.study_id.isin(counts[counts>=20].index)]
    if not set(meta['#SampleID'].astype(str)).issubset(id_to_pos):raise ValueError('metadata IDs absent from BIOM')
    genus_names=sorted({name for name in names if name and name.lower() not in ('uncultured','unclassified')})
    lookup={name:i for i,name in enumerate(genus_names)}
    feature_to_genus=np.array([lookup.get(name,-1) for name in names],dtype=np.int32)
    out=np.zeros((len(genus_names),len(meta)),dtype=np.float32)
    for col,sid in enumerate(meta['#SampleID'].astype(str)):
        i=id_to_pos[sid];start,end=indptr[i:i+2]
        gg=feature_to_genus[indices[start:end]]
        mask=gg>=0
        np.add.at(out[:,col],gg[mask],values[start:end][mask])
    result=pd.DataFrame(out,index=genus_names,columns=meta['#SampleID'].astype(str).tolist())
    result.to_csv(OUT,sep='\t',compression='gzip')
    info={'source_biom':'emp_cr_gg_13_8.release1.biom','source_md5':'5a08ab0811582bbc8f87a923d5c90f73',
          'rows_genus':len(genus_names),'columns_samples':len(meta),'studies':int(meta.study_id.nunique()),
          'zero_genus_mass_samples':int((result.sum(0)==0).sum()),
          'input_biom_sha256':hashlib.sha256(BIOM.read_bytes()).hexdigest(),
          'output_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),
          'status':'outcome_blind_candidate_table_not_external_benchmark',
          'note':'This subset omits exact old-MGnify accessions and missing host IDs; near-duplicate sources, taxonomy compatibility and license remain unverified.'}
    (ROOT/'data/source_family_candidates/EMP/emp_2k_candidate_genus_info.json').write_text(json.dumps(info,indent=2))
    print(info)
if __name__=='__main__':main()
