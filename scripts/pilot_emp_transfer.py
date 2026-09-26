"""Bounded three-study EMP debug pilot; read EMP_PILOT_PROTOCOL.md first."""
from __future__ import annotations
import hashlib,json,sys,time
from pathlib import Path
import numpy as np,pandas as pd,torch
from microtwin.genus_harmonize import terminal_genus
from microtwin.evaluate import fit_predict
from microtwin.data import bray_curtis
ROOT=Path(__file__).resolve().parents[1]
STUDIES=[804,1642,933]
MODELS=['presence_mean','cnode','glv','graphtwin','transformer']

def prepare():
    old=pd.read_csv(ROOT/'data/raw/mgnify/manifest.csv')
    old_ids=set(old.secondary_accession.dropna().astype(str))
    meta=pd.read_csv(ROOT/'data/source_family_candidates/EMP/emp_mapping_subset_2k.tsv',sep='\t',low_memory=False)
    table=pd.read_csv(ROOT/'data/source_family_candidates/EMP/emp_2k_candidate_genus.tsv.gz',sep='\t',index_col=0)
    if not table.columns.is_unique:raise ValueError('duplicate EMP sample columns')
    chunks=[]
    for sid in STUDIES:
        m=meta[meta.study_id==sid]
        if len(m)<60 or m.host_subject_id.isna().any() or m.host_subject_id.nunique()!=len(m):
            raise ValueError(f'study {sid} failed metadata gates')
        if set(m.ebi_accession.astype(str)) & old_ids:raise ValueError(f'study {sid} mirrors old MGnify')
        if m.target_subfragment.nunique()!=1 or m.target_subfragment.iloc[0]!='V4':raise ValueError('incompatible assay')
        ids=m['#SampleID'].astype(str).tolist()
        if not set(ids)<=set(table.columns):raise ValueError('EMP table missing metadata sample')
        chunks.append((sid,ids))
    a,_=terminal_genus(pd.read_csv(ROOT/'data/pilot_external/MGYS00002394_raw.tsv',sep='\t',index_col=0))
    b,_=terminal_genus(pd.read_csv(ROOT/'data/pilot_external/MGYS00006019_raw.tsv',sep='\t',index_col=0))
    vocab=a.index.union(b.index)
    train=pd.concat([a.reindex(vocab,fill_value=0),b.reindex(vocab,fill_value=0)],axis=1).T.to_numpy(float)
    if (train.sum(1)==0).any():raise ValueError('zero train count')
    train/=train.sum(1,keepdims=True);ztr=(train>0).astype(float);ztr/=ztr.sum(1,keepdims=True)
    all_ids=[x for _,ids in chunks for x in ids]
    full=table[all_ids].T.to_numpy(float)
    coverage=table.reindex(vocab,fill_value=0)[all_ids].sum(0)/table[all_ids].sum(0)
    projected=table.reindex(vocab,fill_value=0)[all_ids].T.to_numpy(float)
    good=projected.sum(1)>0
    if not good.all():raise ValueError(f'{sum(~good)} zero-projected samples; report exclusion before scoring')
    zte=(projected>0).astype(float);zte/=zte.sum(1,keepdims=True)
    full/=full.sum(1,keepdims=True)
    return ztr,train,zte,full,vocab,table.index,chunks,coverage

def main():
    torch.set_num_threads(1)
    ztr,ptr,zte,full,vocab,test_names,chunks,coverage=prepare()
    code_head=__import__('subprocess').check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    out={'status':'three_study_source_pilot_not_top_tool_win','code_head_before_result':code_head,
         'protocol_sha256':hashlib.sha256((ROOT/'EMP_PILOT_PROTOCOL.md').read_bytes()).hexdigest(),
         'train_sites':len(ptr),'test_studies':STUDIES,'test_samples':len(zte),'train_genera':len(vocab),
         'test_genera':len(test_names),'minimum_vocab_count_mass':float(coverage.min()),
         'median_vocab_count_mass':float(coverage.median()),'models':{},
         'note':'EMP 2k subset; three metadata-chosen environmental studies, unverified near-duplicate/cluster structure. Descriptive pilot only.'}
    lookup={name:i for i,name in enumerate(test_names)}
    for name in MODELS:
        start=time.time()
        try:
            p=fit_predict(name,ztr,ptr,zte,seed=0)
            if not np.isfinite(p).all() or (p<0).any() or not np.allclose(p.sum(1),1,atol=1e-4):raise ValueError('invalid predictions')
            pred=np.zeros_like(full)
            for j,g in enumerate(vocab):
                if g in lookup:pred[:,lookup[g]]=p[:,j]
            errors=bray_curtis(pred,full)
            metrics={}; pos=0
            for sid,ids in chunks:
                e=errors[pos:pos+len(ids)];metrics[str(sid)]={'n':len(ids),'median_bray_curtis':float(np.median(e)),
                   'errors':dict(zip(ids,map(float,e)))};pos+=len(ids)
            macro=float(np.mean([v['median_bray_curtis'] for v in metrics.values()]))
            out['models'][name]={'status':'ok','seconds':time.time()-start,'study_metrics':metrics,
                                 'macro_study_median_bray_curtis':macro}
        except Exception as e:out['models'][name]={'status':'failed','seconds':time.time()-start,'error':str(e)}
        print(name,out['models'][name]['status'],out['models'][name].get('macro_study_median_bray_curtis'),flush=True)
        (ROOT/'results/pilot_emp_transfer.json').write_text(json.dumps(out,indent=2))
if __name__=='__main__':sys.exit(main())
