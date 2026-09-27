"""Equal-weight mouse-level summary of the locked viewed-cohort two-part diagnostic."""
import json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
KEYS=('sensitivity','specificity','balanced_accuracy','positive_prediction_rate','pair_median_conditional_rmse')

def summarize(cohort):
    source=json.loads((ROOT/f'results/mdsine_dual_{cohort}.json').read_text())
    a=source['methods']['population baseline']['per_mouse']
    b=source['methods']['MDSINE2 no modules']['per_mouse']
    assert set(a)==set(b)
    mice=sorted(a,key=int)
    result={}
    for k in KEYS:
        x=np.array([a[m][k] for m in mice]);y=np.array([b[m][k] for m in mice]);delta=x-y
        result[k]={'baseline_mouse_median':float(np.median(x)),
                   'comparator_mouse_median':float(np.median(y)),
                   'paired_difference_mouse_median':float(np.median(delta)),
                   'baseline_higher_mice':int(sum(delta>0)),
                   'baseline_lower_mice':int(sum(delta<0)),
                   'baseline_equal_mice':int(sum(delta==0))}
    return {'cohort':cohort,'mouse_ids':mice,'n_mice':len(mice),'endpoints':result,
        'interpretation_limit':'Viewed-cohort descriptive mouse-level sensitivity, not a calibrated detection comparison, untouched test, or hypothesis test.'}

if __name__=='__main__':
    for c in ['healthy','uc']:
        out=summarize(c)
        (ROOT/f'results/mdsine_dual_mouse_{c}.json').write_text(json.dumps(out,indent=2)+'\n')
        print(c,{k:(round(v['paired_difference_mouse_median'],4),v['baseline_higher_mice'],v['baseline_lower_mice']) for k,v in out['endpoints'].items()})
