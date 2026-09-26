"""Secondary sensitivity to the locked oral transfer pilot; not a new leaderboard."""
from __future__ import annotations
import json,sys,time,hashlib
from pathlib import Path
import numpy as np,pandas as pd,torch
from microtwin.genus_harmonize import terminal_genus
from microtwin.sample_collapse import collapse_runs
from microtwin.evaluate import fit_predict
from microtwin.data import bray_curtis
ROOT=Path(__file__).resolve().parents[1]
MODELS=['presence_mean','cnode','glv','graphtwin','transformer']
def main():
    torch.set_num_threads(1)
    old,_=terminal_genus(pd.read_csv(ROOT/'data/pilot_external/MGYS00002394_raw.tsv',sep='\t',index_col=0))
    raw=pd.read_csv(ROOT/'data/external_candidate/MGYS00002146_raw.tsv',sep='\t',index_col=0)
    rel=json.load(open(ROOT/'data/external_candidate/MGYS00002146_analysis_relations.json'))
    records=[{'relationships':{'sample':{'data':{'id':r['sample']}},'run':{'data':r['run']},'assembly':{'data':r['assembly']}}} for r in rel]
    test,_=terminal_genus(collapse_runs(raw,records)[0]); projected=test.reindex(old.index,fill_value=0)
    kept=(projected.sum(0)/test.sum(0)); eligible=kept>=.9
    subject=json.load(open(ROOT/'data/external_candidate/MGYS00002146_subject_map.json'))['mapping']
    train=old.T.to_numpy(float);train/=train.sum(1,keepdims=True)
    ztrain=(train>0).astype(float);ztrain/=ztrain.sum(1,keepdims=True)
    test_array=projected.T.to_numpy(float);test_full=test.T.to_numpy(float);test_full/=test_full.sum(1,keepdims=True)
    ztest=(test_array>0).astype(float);ztest/=ztest.sum(1,keepdims=True)
    groups=np.array([subject[x]['subject'] for x in test.columns]);sample_ids=test.columns.tolist()
    output={'status':'secondary_sensitivity_not_external_win','old_pilot':'results/pilot_oral_transfer.json',
       'n_sites':len(sample_ids),'min_coverage':.9,'coverage_rejected_sites':[x for x in sample_ids if not bool(eligible[x])],
       'full_truth_genera':len(test),'train_genera':len(old),'models':{},
       'note':'Full-community BC gives zero predicted mass to test genera absent from train; coverage-gated result is a post-pilot sensitivity, not a new preregistered primary test.'}
    for model in MODELS:
        pred=fit_predict(model,ztrain,train,ztest,seed=0)
        full_pred=np.zeros_like(test_full)
        lookup={g:i for i,g in enumerate(test.index)}
        for j,g in enumerate(old.index):
            if g in lookup:full_pred[:,lookup[g]]=pred[:,j]
        errors=bray_curtis(full_pred,test_full)
        by_person={person:float(np.median(errors[groups==person])) for person in sorted(set(groups))}
        mask=eligible.to_numpy()
        kept_person={person:float(np.median(errors[(groups==person)&mask])) for person in sorted(set(groups[mask]))}
        output['models'][model]={'full_community_site_median':float(np.median(errors)),
           'full_community_person_macro':float(np.mean(list(by_person.values()))),
           'full_community_coverage_gated_person_macro':float(np.mean(list(kept_person.values()))),
           'n_gated_sites':int(mask.sum()),'n_gated_people':len(kept_person),
           'errors':dict(zip(sample_ids,map(float,errors)))}
        print(model,output['models'][model]['full_community_person_macro'],flush=True)
        (ROOT/'results/pilot_oral_sensitivity.json').write_text(json.dumps(output,indent=2))
if __name__=='__main__':sys.exit(main())
