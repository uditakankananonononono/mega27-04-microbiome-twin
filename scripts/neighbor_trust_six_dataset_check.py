"""Fixed-rule, already-viewed internal diagnostic; not an external benchmark."""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from microtwin.data import DATASETS, load, bray_curtis
from microtwin.evaluate import kfold_indices
from microtwin.neighborhood_twin import NeighborhoodTrustTwin


def run():
    rows=[]
    for name in DATASETS:
        z,p=load(name); error={k:np.full(len(z),np.nan) for k in ('prior','local','trust')}
        alpha=np.full(len(z),np.nan);fallback=np.zeros(len(z),dtype=bool);abstain=np.zeros(len(z),dtype=bool)
        for test in kfold_indices(len(z), min(10,len(z)),seed=0):
            train=np.setdiff1d(np.arange(len(z)),test)
            model=NeighborhoodTrustTwin().fit(z[train],p[train])
            for i in test:
                try:
                    pred,detail=model.predict_with_details(z[i:i+1])
                except ValueError as e:
                    if 'present query taxon absent' not in str(e):raise
                    abstain[i]=True
                    continue
                for label,estimate in [('prior',detail['prior']),('local',detail['local']),('trust',pred)]:
                    error[label][i]=bray_curtis(estimate,p[i:i+1])[0]
                alpha[i]=detail['alpha'][0];fallback[i]=detail['fallback'][0]
        covered=~abstain
        if not covered.any() or not all(np.isfinite(v[covered]).all() for v in (*error.values(),alpha)):
            raise ValueError('incomplete covered prediction')
        src=ROOT/'data/raw/cnode'/f'{name}.csv'
        rows.append({'dataset':name,'samples':len(z),'taxa':z.shape[1],'covered':int(covered.sum()),'abstentions':int(abstain.sum()),
                     'input_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
                     'median_bray_curtis':{k:float(np.median(v[covered])) for k,v in error.items()},
                     'mean_bray_curtis':{k:float(np.mean(v[covered])) for k,v in error.items()},
                     'trust_minus_prior_median_sample_error':float(np.median(error['trust'][covered]-error['prior'][covered])),
                     'trust_minus_prior_difference_of_medians':float(np.median(error['trust'][covered])-np.median(error['prior'][covered])),
                     'alpha_median':float(np.median(alpha[covered])),'alpha_min':float(alpha[covered].min()),
                     'alpha_max':float(alpha[covered].max()),'fallbacks':int(fallback[covered].sum())})
    return {'protocol':'results/PREREG_20260928_neighbor_trust_twin.md',
            'scope':'six previously viewed cNODE datasets; internal 10-fold, no family/source independence, no algorithmic-priority or top-tool claim',
            'dataset_median_wins_vs_prior':sum(r['median_bray_curtis']['trust']<r['median_bray_curtis']['prior'] for r in rows),
            'rows':rows}

if __name__=='__main__':
    d=run();out=ROOT/'results/neighbor_trust_six_dataset_check.json';out.write_text(json.dumps(d,indent=2)+'\n')
    print(out);print(json.dumps(d,indent=2))
