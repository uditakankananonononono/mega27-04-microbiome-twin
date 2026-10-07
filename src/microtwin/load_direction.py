"""Absolute-fold feasibility under explicit fraction and load-ratio boxes."""
from math import isfinite


def _interval(x, *, fraction=False):
    if not isinstance(x,(list,tuple)) or len(x)!=2:
        raise ValueError('two endpoints required')
    if any(type(v) not in (int,float) or not isfinite(v) or v<=0 for v in x):
        raise ValueError('finite strictly positive endpoints required; zeros need detection model')
    lo,hi=map(float,x)
    if lo>hi or (fraction and hi>1):
        raise ValueError('ordered bounds required; fractions at most one')
    return lo,hi


def bound_absolute_fold(before, during, load_ratio, *, measurement_compatible):
    """Box extremizers only, not a confidence or causal certificate."""
    if type(measurement_compatible) is not bool:
        raise ValueError('explicit measurement compatibility boolean required')
    b=_interval(before,fraction=True);d=_interval(during,fraction=True)
    out={'status':'abstain','absolute_fold_bounds':None,'witnesses':[],
         'measurement_compatible':measurement_compatible,'independent_validation':False,
         'causal_interpretation':False,'clinical_eligible':False,
         'scope':'Cartesian interval feasibility assuming true compatible fractions; no probabilistic coverage or biological provenance verification'}
    if load_ratio is None:
        out['reason']='unknown total load ratio'
        return out
    q=_interval(load_ratio)
    lo=d[0]*q[0]/b[1];hi=d[1]*q[1]/b[0]
    if not isfinite(lo) or not isfinite(hi) or lo<=0:
        raise ValueError('fold computation overflow/underflow')
    out['absolute_fold_bounds']=[lo,hi]
    if not measurement_compatible:
        out['reason']='unverified measurement compatibility'
        return out
    if lo>1:out['status']='increase_under_supplied_box'
    elif hi<1:out['status']='decrease_under_supplied_box'
    elif lo<1<hi:
        out['status']='opposite_direction_feasibility_witness'
        out['witnesses']=[{'before_fraction':b[1],'during_fraction':d[0],'load_ratio':q[0],'absolute_fold':lo},
                          {'before_fraction':b[0],'during_fraction':d[1],'load_ratio':q[1],'absolute_fold':hi}]
    else:out['reason']='bounds touch or equal no-change fold one'
    return out
