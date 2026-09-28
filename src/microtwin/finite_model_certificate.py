"""Witness existence in an explicitly supplied finite set of 3-species gLVs.

No candidate fitting, parameter inference, continuous-family completeness, or
biological intervention prediction is performed here.
"""
import numpy as np


def _check(a,r,baseline):
    a=np.asarray(a,dtype=float);r=np.asarray(r,dtype=float)
    if a.shape!=(3,3) or r.shape!=(3,) or not np.isfinite(a).all() or not np.isfinite(r).all():
        raise ValueError('finite 3x3 A and length-3 r required')
    try:post2=np.linalg.solve(a[:2,:2],-r[:2])
    except np.linalg.LinAlgError as e:raise ValueError('singular survivor system') from e
    if not np.isfinite(post2).all() or (post2<=0).any():raise ValueError('nonpositive survivor equilibrium')
    baseline_residual=float(np.max(np.abs(baseline*(r+a@baseline))))
    survivor_residual=float(np.max(np.abs(post2*(r[:2]+a[:2,:2]@post2))))
    before_stability=float(np.max(np.linalg.eigvals(np.diag(baseline)@a).real))
    after_stability=float(np.max(np.linalg.eigvals(np.diag(post2)@a[:2,:2]).real))
    if (baseline_residual>1e-8 or survivor_residual>1e-8 or
            before_stability>=-1e-7 or after_stability>=-1e-7):
        raise ValueError('candidate inconsistent with observed/stable equilibria')
    return {'interaction_matrix':a.tolist(),'intrinsic_rates':r.tolist(),
            'baseline':baseline.tolist(),'post_removal':[float(post2[0]),float(post2[1]),0.],
            'target_change':float(post2[0]-baseline[0]),
            'max_baseline_residual':baseline_residual,'max_survivor_residual':survivor_residual,
            'max_before_jacobian_real_eigenvalue':before_stability,
            'max_after_jacobian_real_eigenvalue':after_stability}


def certify_finite_candidates(candidates, baseline):
    x=np.asarray(baseline,dtype=float)
    if x.shape!=(3,) or not np.isfinite(x).all() or (x<=0).any():
        raise ValueError('finite positive three-species baseline required')
    if not isinstance(candidates,(tuple,list)) or not 1<=len(candidates)<=10000:
        raise ValueError('1 to 10000 candidate models required')
    positives=[];negatives=[];zeros=0;rejected=0
    for i,c in enumerate(candidates):
        try:
            if not isinstance(c,dict) or 'A' not in c or 'r' not in c:raise ValueError('invalid candidate schema')
            record=_check(c['A'],c['r'],x);record['candidate_index']=i
        except (ValueError,TypeError,OverflowError,np.linalg.LinAlgError):
            rejected+=1;continue
        change=record['target_change']
        if change>1e-6:positives.append(record)
        elif change< -1e-6:negatives.append(record)
        else:zeros+=1
    witness=[positives[0],negatives[0]] if positives and negatives else []
    return {'status':'opposite_sign_witness' if witness else 'abstain_no_witness_in_finite_set',
            'candidate_count':len(candidates),'valid_count':len(candidates)-rejected,
            'rejected_count':rejected,'positive_count':len(positives),
            'negative_count':len(negatives),'near_zero_count':zeros,
            'witnesses':witness,
            'scope':'existence among submitted finite models only; abstention does not prove continuous-family sign certainty; constructed systems are not biological evidence; basin reachability after removal is not checked'}
