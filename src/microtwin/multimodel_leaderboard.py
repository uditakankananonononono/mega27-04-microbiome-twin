"""Validation-selected, family-paired multi-model statistics, not certification.

The caller supplies already measured same-task losses. Source labels, rights,
untouched status and budget fairness require separate inspection.
"""
from __future__ import annotations
import itertools
import math
import numpy as np
from .leaderboard_stats import compare_by_study


def _validated(errors, families):
    if not isinstance(errors, dict) or len(errors) < 2:
        raise ValueError('at least two named model loss vectors required')
    if any(not isinstance(k, str) or not k or k != k.strip() for k in errors):
        raise ValueError('nonblank trimmed model names required')
    ids = list(families)
    if not ids or any(not isinstance(x, str) or not x or x != x.strip() for x in ids):
        raise ValueError('nonblank trimmed source-family labels required')
    vectors = {}
    for model, values in errors.items():
        a = np.asarray(values, dtype=float)
        if a.shape != (len(ids),) or not np.isfinite(a).all() or (a < 0).any() or (a > 1).any():
            raise ValueError('aligned finite Bray-Curtis errors in [0,1] required for every model')
        vectors[model] = a
    return vectors, ids


def freeze_comparator(validation_errors, validation_families, *, candidate):
    """Choose smallest macro-family median validation loss, lexical tie break.

    Selection never reads test losses. The returned record must be retained
    before final test inspection; this function cannot authenticate its timing.
    """
    vectors, ids = _validated(validation_errors, validation_families)
    if candidate not in vectors:
        raise ValueError('candidate must be a declared model')
    families = sorted(set(ids))
    if len(families) < 2:
        raise ValueError('at least two validation source families required')
    scores = {m: float(np.mean([np.median(a[np.array(ids) == f]) for f in families]))
              for m, a in vectors.items()}
    selected = min((m for m in scores if m != candidate), key=lambda m: (scores[m], m))
    return {'schema': 'validation_comparator_v1', 'candidate': candidate,
            'models': sorted(vectors), 'validation_families': families,
            'validation_macro_losses': scores, 'selected_comparator': selected,
            'selection_rule': 'minimum_macro_family_median_then_lexical',
            'timing_verified': False}


def _holm(p_values):
    ordered = sorted(p_values, key=lambda k: (p_values[k], k))
    running = 0.0
    adjusted = {}
    for i, name in enumerate(ordered):
        running = max(running, min(1.0, (len(ordered)-i)*p_values[name]))
        adjusted[name] = running
    return adjusted


def compare_frozen_models(selection, test_errors, test_families, *, n_boot=5000, seed=0):
    """Exact two-sided paired sign-flip tests on independent-family medians.

    Requires 2-16 submitted test families to bound exhaustive 2**n enumeration.
    Symmetry/exchangeability of paired differences is an inferential assumption,
    not established by matching family labels. No subject-weighted pseudoreplication.
    """
    if type(n_boot) is not int or not 0 <= n_boot <= 10000 or type(seed) is not int or seed < 0:
        raise ValueError("bounded bootstrap count and nonnegative integer seed required")
    vectors, ids = _validated(test_errors, test_families)
    expected = {'schema','candidate','models','validation_families','validation_macro_losses',
                'selected_comparator','selection_rule','timing_verified'}
    if not isinstance(selection, dict) or set(selection) != expected:
        raise ValueError('complete frozen validation comparator record required')
    if selection['schema'] != 'validation_comparator_v1' or selection['selection_rule'] != 'minimum_macro_family_median_then_lexical':
        raise ValueError('invalid selection schema or rule')
    if type(selection['timing_verified']) is not bool:
        raise ValueError('selection timing marker must be boolean; it is not authenticated')
    models = selection['models']
    if models != sorted(vectors):
        raise ValueError('all frozen models must have complete test results; no failed model may be silently dropped')
    candidate = selection['candidate']
    selected = selection['selected_comparator']
    if candidate not in models or selected not in models or selected == candidate:
        raise ValueError('invalid candidate or comparator')
    scores = selection['validation_macro_losses']
    if not isinstance(scores,dict) or set(scores)!=set(models) or any(type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=1 for v in scores.values()):
        raise ValueError('valid complete validation losses required')
    if selected != min((m for m in models if m != candidate), key=lambda m:(scores[m],m)):
        raise ValueError('comparator contradicts frozen validation selection')
    val = selection['validation_families']
    if not isinstance(val,list) or len(val)<2 or any(not isinstance(f,str) or not f or f!=f.strip() for f in val) or len(set(val))!=len(val):
        raise ValueError('valid unique validation families required')
    families = sorted(set(ids))
    if set(val) & set(families):
        raise ValueError('validation/test source-family overlap')
    n = len(families)
    if not 2 <= n <= 16:
        raise ValueError('exact inference needs 2-16 test source families')
    medians = {m: np.array([np.median(a[np.array(ids)==f]) for f in families]) for m,a in vectors.items()}
    signs = np.asarray(list(itertools.product((-1,1),repeat=n)),dtype=float)
    comparisons = {}
    for baseline in models:
        if baseline == candidate:
            continue
        delta = medians[candidate]-medians[baseline]
        observed = float(delta.mean())
        random = (signs @ delta)/n
        p = float(np.mean(np.abs(random) >= abs(observed)-1e-14))
        comparisons[baseline] = {'macro_delta_candidate_minus_baseline':observed,
                                 'p_two_sided_exact_sign_flip':p}
    adj = _holm({m:r['p_two_sided_exact_sign_flip'] for m,r in comparisons.items()})
    for m in comparisons:
        comparisons[m]['p_holm'] = adj[m]
    primary = compare_by_study(vectors[candidate], vectors[selected], ids, n_boot=n_boot, seed=seed)
    return {'primary_selected_comparator_statistic':primary,
            'status':'submitted_multimodel_statistics_only', 'n_test_rows':len(ids),
            'n_test_family_labels':n,'selected_comparator':selected,
            'macro_family_median_losses':{m:float(a.mean()) for m,a in medians.items()},
            'comparisons':comparisons,'external_win_certified':False,
            'limitations':['Submitted family labels and losses are not authenticated.',
                           'Selection timing, source independence, rights and matched budgets require inspection.',
                           'Exact sign-flip inference assumes symmetric exchangeable paired family differences.',
                           'Primary interval is family-level; Holm tests are supplementary, not certification.',
                           'This is composition prediction, not causal interaction or clinical evidence.']}
