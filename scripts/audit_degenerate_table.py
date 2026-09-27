"""Reproduce raw-to-audit dimensions for the known zero-error MGnify table."""
import hashlib,json
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
STUDY='MGYS00006086'

def run():
    manifest=pd.read_csv(ROOT/'data/raw/mgnify/manifest.csv')
    row=manifest[manifest.study==STUDY]
    if len(row)!=1:raise ValueError('study not unique in manifest')
    row=row.iloc[0]
    path=ROOT/row.file
    if path.exists():
        raw=pd.read_csv(path,sep='\t',index_col=0).T
        source_path=str(row.file)
        source_hash=hashlib.sha256(path.read_bytes()).hexdigest()
    else:
        # Reconstruct the archived fetch transform from the exact pinned manifest URL.
        # The archived derived TSV is not committed in this repository.
        import io,urllib.request
        with urllib.request.urlopen(row.source_url,timeout=35) as response: blob=response.read()
        if len(blob)>60_000_000:raise ValueError('source size bound exceeded')
        source_hash=hashlib.sha256(blob).hexdigest()
        t=pd.read_csv(io.BytesIO(blob),sep='\t',index_col=0)
        t=t.select_dtypes('number')
        genus=[(i.split(';g__')[1].split(';')[0] if ';g__' in i and i.split(';g__')[1].split(';')[0] else None) for i in t.index]
        t.index=genus;t=t[t.index.notnull()].groupby(level=0).sum()
        t=t.loc[:,t.sum(0)>0]
        raw=t.T
        source_path=str(row.source_url)
    if raw.shape != (int(row.n_samples),int(row.n_genera)):
        raise ValueError(f'reconstructed table does not match manifest dimensions: {raw.shape}')
    x=raw.loc[raw.sum(1)>0]
    a={'raw_samples':int(len(raw)),'raw_taxa':int(raw.shape[1]),
       'nonzero_samples':int(len(x)),'metadata_manifest_n_genera':int(row.n_genera)}
    prev=(x>0).mean(0)
    x=x.loc[:,prev>=.05];x=x.loc[x.sum(1)>0]
    a['post_prevalence_taxa']=int(x.shape[1]);a['post_prevalence_samples']=int(len(x))
    if x.shape[1]>150:x=x[x.columns[np.argsort(-(x>0).mean(0).values)[:150]]]
    x=x.loc[x.sum(1)>0]
    if len(x)>400:x=x.sample(400,random_state=0)
    a['analyzed_samples']=int(len(x));a['analyzed_taxa']=int(x.shape[1])
    if not len(x) or not x.shape[1]:raise ValueError('empty analyzed table')
    p=x.to_numpy(float);p/=p.sum(1,keepdims=True)
    b=p>0
    a['unique_presence_assemblages']=int(np.unique(b,axis=0).shape[0])
    a['taxa_present_count_distribution']={str(int(k)):int(v) for k,v in zip(*np.unique(b.sum(1),return_counts=True))}
    a['unique_composition_vectors_rounded_12dp']=int(np.unique(np.round(p,12),axis=0).shape[0])
    a['median_max_taxon_fraction']=float(np.median(p.max(1)))
    a['all_samples_same_presence']=bool(a['unique_presence_assemblages']==1)
    a['single_taxon_sample_fraction']=float((b.sum(1)==1).mean())
    old=pd.read_csv(ROOT/'results/mgnify_audit_fdr.csv').query('study==@STUDY')
    if len(old)!=1 or old.iloc[0]['n']!=len(x) or old.iloc[0]['taxa']!=x.shape[1]:
        raise ValueError('archive dimensions do not match preprocessing')
    a['archived_median_prior']=float(old.iloc[0].median_prior)
    a['archived_median_interaction']=float(old.iloc[0].median_interaction)
    return {'study':STUDY,'source_path':source_path,'source_sha256':source_hash,
            'aggregates':a,'scope':'viewed source QC; no refit, p-value change, or exclusion from 160-study BH audit'}
if __name__=='__main__':
    x=run();(ROOT/'results/audit_degenerate_table.json').write_text(json.dumps(x,indent=2)+'\n');print(json.dumps(x,indent=2))
