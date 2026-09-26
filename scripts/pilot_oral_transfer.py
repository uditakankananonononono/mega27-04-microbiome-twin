"""One-study oral-to-oral debug pilot; see PILOT_TRANSFER_PROTOCOL.md."""
from __future__ import annotations

import hashlib,json,sys,time
from pathlib import Path
import numpy as np,pandas as pd,torch
from microtwin.genus_harmonize import terminal_genus
from microtwin.sample_collapse import collapse_runs
from microtwin.transfer_coverage import vocabulary_coverage
from microtwin.evaluate import fit_predict
from microtwin.data import bray_curtis

ROOT=Path(__file__).resolve().parents[1]
MODELS=['presence_mean','cnode','glv','graphtwin','transformer']

def load():
    train,_=terminal_genus(pd.read_csv(ROOT/'data/pilot_external/MGYS00002394_raw.tsv',sep='\t',index_col=0))
    test_raw=pd.read_csv(ROOT/'data/external_candidate/MGYS00002146_raw.tsv',sep='\t',index_col=0)
    rel=json.load(open(ROOT/'data/external_candidate/MGYS00002146_analysis_relations.json'))
    records=[{'relationships':{'sample':{'data':{'id':r['sample']}},'run':{'data':r['run']},
               'assembly':{'data':r['assembly']}}} for r in rel]
    pooled,rr=collapse_runs(test_raw,records)
    test,_=terminal_genus(pooled)
    coverage=vocabulary_coverage(train.index,test)
    # Preserve train vocabulary order; no test-outcome feature selection.
    t=test.reindex(train.index,fill_value=0)
    good=t.sum(0)>0
    excluded=t.columns[~good].tolist()
    t=t.loc[:,good]
    tr=train.T.to_numpy(dtype=float);te=t.T.to_numpy(dtype=float)
    if (tr.sum(1)<=0).any():raise ValueError('zero-mass training sample')
    trp=tr/tr.sum(1,keepdims=True);tep=te/te.sum(1,keepdims=True)
    ztr=(trp>0).astype(float);zte=(tep>0).astype(float)
    ztr/=ztr.sum(1,keepdims=True);zte/=zte.sum(1,keepdims=True)
    person=json.load(open(ROOT/'data/external_candidate/MGYS00002146_subject_map.json'))['mapping']
    groups=[person[s]['subject'] for s in t.columns]
    return ztr,trp,zte,tep,t.columns.tolist(),groups,excluded,coverage,rr

def main():
    torch.set_num_threads(1)
    ztr,ptr,zte,pte,ids,groups,excluded,coverage,rr=load()
    outcome={'status':'one_study_debug_pilot_not_external_win','train':'MGYS00002394','test':'MGYS00002146',
      'train_samples':len(ptr),'test_sites':len(pte),'test_people':len(set(groups)),
      'excluded_zero_mass_sites':excluded,'coverage':coverage,'run_mapping':rr,'models':{},
      'protocol_sha256':hashlib.sha256((ROOT/'PILOT_TRANSFER_PROTOCOL.md').read_bytes()).hexdigest(),
      'source_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in
        ['data/pilot_external/MGYS00002394_raw.tsv','data/external_candidate/MGYS00002146_raw.tsv']}}
    for name in MODELS:
        started=time.time()
        try:
            p=fit_predict(name,ztr,ptr,zte,seed=0)
            if p.shape!=pte.shape or not np.isfinite(p).all() or (p<0).any() or not np.allclose(p.sum(1),1,atol=1e-4):
                raise ValueError('invalid prediction simplex')
            errors=bray_curtis(p,pte)
            person_errors={person:float(np.median(errors[np.asarray(groups)==person])) for person in sorted(set(groups))}
            outcome['models'][name]={'status':'ok','seconds':time.time()-started,'median_site_bray_curtis':float(np.median(errors)),
                 'macro_person_median_bray_curtis':float(np.mean(list(person_errors.values()))),
                 'site_errors':dict(zip(ids,map(float,errors))),'person_median_errors':person_errors}
        except Exception as e:
            outcome['models'][name]={'status':'failed','seconds':time.time()-started,'error':str(e)}
        print(name,outcome['models'][name]['status'],outcome['models'][name].get('macro_person_median_bray_curtis'),flush=True)
        (ROOT/'results/pilot_oral_transfer.json').write_text(json.dumps(outcome,indent=2))
    return 0
if __name__=='__main__':sys.exit(main())
