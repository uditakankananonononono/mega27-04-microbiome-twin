"""Exact witness/abstention in a narrow analytic three-species gLV family.

Not a data-fitted, general gLV, relative-abundance or patient-level certificate.
See results/PREREG_20260928_counterfactual_ambiguity_certificate.md.
"""
import math
import numpy as np


def _model(c):
    a=np.diag([-1.,-1.,-1.]);a[0,2]=c
    r=np.array([1.-c,1.,1.]);x=np.ones(3)
    residual=x*(r+a@x)
    jac=np.diag(x)@a
    post=np.array([1.-c,1.,0.])
    post_residual=post[:2]*(r[:2]+a[:2,:2]@post[:2])
    post_jac=np.diag(post[:2])@a[:2,:2]
    baseline_eig=float(max(np.linalg.eigvals(jac).real))
    post_eig=float(max(np.linalg.eigvals(post_jac).real))
    if (max(abs(residual))>1e-9 or max(abs(post_residual))>1e-9
            or baseline_eig>=-1e-9 or post_eig>=-1e-9 or (post[:2]<=0).any()):
        raise ValueError('candidate fails equilibrium/stability verification')
    return {'interaction_matrix':a.tolist(),'intrinsic_rates':r.tolist(),
            'observed_equilibrium':x.tolist(),'post_removal_equilibrium':post.tolist(),
            'target_change':float(post[0]-x[0]),
            'max_abs_baseline_residual':float(max(abs(residual))),
            'max_abs_post_removal_residual':float(max(abs(post_residual))),
            'max_baseline_jacobian_real_eigenvalue':baseline_eig,
            'max_post_removal_jacobian_real_eigenvalue':post_eig}


def certify_three_species_removal(lower,upper):
    """Prove *existence* of opposite signs within the specified c interval.

    Abstention means no strict opposite-sign witness exists in this family, not
    that an intervention is safe or causally known in a real microbiome.
    """
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v)
           for v in (lower,upper)) or lower>upper or lower<-.8 or upper>.8:
        raise ValueError('finite ordered c interval inside [-0.8,0.8] required')
    l,u=_model(float(lower)),_model(float(upper))
    exists=l['target_change']>1e-6 and u['target_change']< -1e-6
    return {'status':'opposite_sign_witness' if exists else 'no_opposite_sign_witness_in_toy_family',
            'interaction_parameter_interval':[float(lower),float(upper)],
            'generic_free_parameter_flag':lower!=upper,
            'witnesses':[{'c':float(lower),**l},{'c':float(upper),**u}] if exists else [],
            'endpoint_verification':{'lower_target_change':l['target_change'],
                                     'upper_target_change':u['target_change'],
                                     'lower_max_baseline_jacobian_real_eigenvalue':l['max_baseline_jacobian_real_eigenvalue'],
                                     'upper_max_baseline_jacobian_real_eigenvalue':u['max_baseline_jacobian_real_eigenvalue']},
            'scope':'exact analytical existence in constrained synthetic three-species absolute-abundance gLV only; no inference of real parameters, no tested basin reachability, clinical or intervention forecast'}
