"""Frozen local-parameter inventory, not a capacity-causal experiment."""
import json
from pathlib import Path
import numpy as np
from microtwin.data import load
from microtwin.evaluate import EPOCHS
from microtwin.models import CNODE, GLVSteady, GraphTwin
ROOT=Path(__file__).resolve().parents[1]
DATASETS=('Drosophila_Gut','Soil_Vitro','Human_Oral','Human_Gut','Ocean','Soil_Vivo')
MODELS=('presence_mean','cnode','glv','graphtwin')

def run():
    rows=[]
    for name in DATASETS:
        Z,P=load(name)
        file=ROOT/f'results/bench_{name}_presence_mean_cnode_glv_graphtwin_k10.json'
        old=json.loads(file.read_text())
        n=len(Z);taxa=Z.shape[1]
        if old['n']!=n or old['taxa']!=taxa or old['k']!=10 or set(old['errors'])!=set(MODELS):
            raise ValueError(f'archived source/result mismatch for {name}')
        fitted={'presence_mean':taxa,
                'cnode':sum(p.numel() for p in CNODE(taxa).parameters() if p.requires_grad),
                'glv':sum(p.numel() for p in GLVSteady(taxa).parameters() if p.requires_grad),
                'graphtwin':sum(p.numel() for p in GraphTwin(taxa,prior=P.mean(0)).parameters() if p.requires_grad)}
        e={m:np.asarray(old['errors'][m],dtype=float) for m in MODELS}
        if any(len(x)!=n or not np.isfinite(x).all() for x in e.values()):
            raise ValueError(f'error vector invalid for {name}')
        if any(not np.isclose(np.median(e[m]),old['median'][m],atol=1e-12) for m in MODELS):
            raise ValueError(f'median mismatch for {name}')
        for m in MODELS:
            rows.append({'dataset':name,'samples':n,'taxa':taxa,'model':m,
                         'fitted_scalars':int(fitted[m]),
                         'gradient_epochs':EPOCHS.get(m,0),
                         'nominal_learning_rate':0.005 if m=='graphtwin' else (None if m=='presence_mean' else 0.01),
                         'archived_10fold_median_bray_curtis':float(np.median(e[m])),
                         'strictly_lower_error_than_presence_mean_samples':int(np.sum(e[m]<e['presence_mean'])),
                         'strictly_higher_error_samples':int(np.sum(e[m]>e['presence_mean']))})
    return {'rows':rows,'scope':'old viewed local 10-fold folds, parameter count and nominal epochs only; no matched-budget or source-transfer claim',
            'method':'default local model classes; buffers excluded; PresenceMean counts training taxon means'}
if __name__=='__main__':
    out=run();(ROOT/'results/capacity_inventory.json').write_text(json.dumps(out,indent=2)+'\n')
    for r in out['rows']:print(r['dataset'],r['model'],r['fitted_scalars'],round(r['archived_10fold_median_bray_curtis'],3))
