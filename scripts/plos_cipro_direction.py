"""Frozen 3-subject, OTU-relative-abundance direction baselines; no causal claim."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
import xlrd

def predict(pre,delta,held):
    donors=[i for i in range(3) if i!=held]
    distances=[np.abs(pre[held]-pre[i]).sum()/np.abs(pre[held]+pre[i]).sum() for i in donors]
    nearest=min(zip(distances,donors))[1]
    return {'median_other2':np.median(delta[donors],axis=0),'nearest_pre_donor':delta[nearest].copy(),'decline_only':-np.ones(pre.shape[1])},nearest

def main(path,out):
    s=xlrd.open_workbook(path).sheet_by_index(0);headers=s.row_values(0);assert s.nrows==5671
    pairs=[('A2c','A3b'),('B2','B3'),('C2','C3')]
    def column(label):
        x=np.array([s.cell_value(i,headers.index(label)) for i in range(1,s.nrows)],float)
        assert np.isfinite(x).all() and (x>=0).all() and x.sum()>0
        return x/x.sum()
    pre=np.array([column(a) for a,b in pairs]);post=np.array([column(b) for a,b in pairs]);delta=post-pre;results=[]
    for held in range(3):
        preds,nearest=predict(pre,delta,held)
        altered=delta.copy();altered[held]=12345
        assert all(np.array_equal(v,predict(pre,altered,held)[0][k]) for k,v in preds.items()),'held outcome leak'
        eligible=np.abs(delta[held])>=.001;assert eligible.any()
        methods={}
        for name,p in preds.items():
            nonzero=eligible&(np.abs(p)>1e-12);correct=(np.sign(p)==np.sign(delta[held]))&(np.abs(p)>1e-12)
            methods[name]={'accuracy_zero_wrong':float(correct[eligible].mean()),'coverage':float(nonzero.sum()/eligible.sum()),'conditional_nonzero_accuracy':float(correct[nonzero].mean()) if nonzero.any() else None,'correct':int(correct[eligible].sum())}
        results.append({'subject':'ABC'[held],'eligible_otus':int(eligible.sum()),'nearest_donor':'ABC'[nearest],'methods':methods})
    macro={name:float(np.mean([r['methods'][name]['accuracy_zero_wrong'] for r in results])) for name in preds}
    result={'question':'small-n day -1 to +5 ciprofloxacin OTU direction check','n_subjects':3,'otus':5670,'source_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),'per_subject':results,'macro_accuracy_zero_wrong':macro,'nearest_minus_median':macro['nearest_pre_donor']-macro['median_other2'],'held_out_outcome_invariance_test':'PASS','causal_effect_claim':False,'generalization_claim':False,'benchmark_win_certified':False}
    Path(out).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main(*sys.argv[1:])
