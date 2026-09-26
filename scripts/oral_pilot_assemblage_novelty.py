"""Post-hoc assemblage novelty/error diagnostic on a viewed oral pilot.

Only source-unseen assemblage distances are used as inputs; this does not
supply missing site metadata or make an untouched external benchmark.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / 'results/pilot_oral_transfer.json'
SUBJECTS = ROOT / 'data/external_candidate/MGYS00002146_subject_map.json'
TRAIN = ROOT / 'data/pilot_external/MGYS00002394_raw.tsv'
TEST = ROOT / 'data/external_candidate/MGYS00002146_raw.tsv'


def summarize(seed=2026, resamples=10000):
    import sys
    sys.path.insert(0, str(ROOT/'scripts'))
    from pilot_oral_transfer import load
    pilot = json.loads(PILOT.read_text())
    if pilot['status'] != 'one_study_debug_pilot_not_external_win' or pilot['test_people'] != 58:
        raise ValueError('unexpected pilot data')
    for key, path in [(str(TRAIN.relative_to(ROOT)), TRAIN), (str(TEST.relative_to(ROOT)), TEST)]:
        if hashlib.sha256(path.read_bytes()).hexdigest() != pilot['source_sha256'][key]:
            raise ValueError('source abundance file checksum changed')
    ztr, ptr, zte, pte, ids, groups, excluded, coverage, rr = load()
    if len(ids) != 87 or len(set(groups)) != 58 or excluded or ztr.shape[1] != zte.shape[1]:
        raise ValueError('unexpected assemblage units')
    if set(ids) != set(json.loads(SUBJECTS.read_text())['mapping']):
        raise ValueError('person mapping mismatch')
    # Normalized assemblages are binary >0; Jaccard distance to nearest
    # training assemblage. Neither test abundance magnitude nor errors choose
    # the nearest source input.
    a, b = ztr > 0, zte > 0
    intersection = b.astype(int) @ a.astype(int).T
    union = b.sum(1)[:,None] + a.sum(1)[None,:] - intersection
    nearest = np.min(1-intersection/union,axis=1)
    grp = np.asarray(groups)
    per_person = {g: float(np.median(nearest[grp==g])) for g in sorted(set(groups))}
    ordered = sorted(per_person)
    novelty = np.array([per_person[g] for g in ordered])
    cut = float(np.median(novelty))
    high = novelty > cut
    if high.sum()<2 or (~high).sum()<2:
        raise ValueError('too few distinct novelty groups')
    rng = np.random.default_rng(seed)
    richness = b.sum(1)
    person_richness = np.array([np.median(richness[grp==g]) for g in ordered])
    # Whole-person bootstrap of a descriptive linear sensitivity.
    unadjusted = np.column_stack([np.ones(len(ordered)), novelty])
    adjusted = np.column_stack([np.ones(len(ordered)), novelty, person_richness])
    adjustment_rng = np.random.default_rng(seed)
    draws = adjustment_rng.integers(len(ordered), size=(resamples, len(ordered)))
    out = {'status': 'viewed_one_study_posthoc_assemblage_novelty_diagnostic',
           'pilot_sha256':hashlib.sha256(PILOT.read_bytes()).hexdigest(),
           'subject_map_sha256':hashlib.sha256(SUBJECTS.read_bytes()).hexdigest(),
           'train_source_sha256':pilot['source_sha256'][str(TRAIN.relative_to(ROOT))],
           'test_source_sha256':pilot['source_sha256'][str(TEST.relative_to(ROOT))],
           'test_sites':len(ids),'people':len(ordered),
           'nearest_train_assemblage_jaccard_person_median':float(np.median(novelty)),
           'high_novelty_cut_strict_greater_than_person_median':cut,
           'high_novelty_people':int(high.sum()),'low_or_equal_novelty_people':int((~high).sum()),
           'median_person_taxon_richness_high_novelty':float(np.median(person_richness[high])),
           'median_person_taxon_richness_low_or_equal_novelty':float(np.median(person_richness[~high])),
           'median_person_jaccard_distance_high_novelty':float(np.median(novelty[high])),
           'median_person_jaccard_distance_low_or_equal_novelty':float(np.median(novelty[~high])),
           'pearson_novelty_taxon_richness':float(np.corrcoef(novelty,person_richness)[0,1]),
           'bootstrap_unit':'person within each post-hoc novelty stratum',
           'resamples':resamples,'seed':seed,'models':{},
           'scope':'Post-hoc within the one already viewed oral study. Median split is selected using only query assemblages, not outcome errors, but novelty groups and species names remain one source; intervals are descriptive and model multiplicity uncorrected. Richness adjustment is a linear sensitivity only and does not identify ecological interactions.'}
    prior=pilot['models']['presence_mean']['person_median_errors']
    for name,r in pilot['models'].items():
        if r['status']!='ok' or set(r['person_median_errors'])!=set(ordered):
            raise ValueError('unpaired model predictions')
        dif=np.array([r['person_median_errors'][p]-prior[p] for p in ordered])
        lo,hi=dif[~high],dif[high]
        draw_lo=rng.integers(len(lo),size=(resamples,len(lo)))
        draw_hi=rng.integers(len(hi),size=(resamples,len(hi)))
        contrast=hi[draw_hi].mean(1)-lo[draw_lo].mean(1)
        simple_slope = np.linalg.lstsq(unadjusted, dif, rcond=None)[0][1]
        adjusted_slope = np.linalg.lstsq(adjusted, dif, rcond=None)[0][1]
        boot_simple = np.array([np.linalg.lstsq(unadjusted[ix],dif[ix],rcond=None)[0][1] for ix in draws])
        boot_adjusted = np.array([np.linalg.lstsq(adjusted[ix],dif[ix],rcond=None)[0][1] for ix in draws])
        out['models'][name]={'low_novelty_model_minus_prior_mean':float(lo.mean()),
                             'high_novelty_model_minus_prior_mean':float(hi.mean()),
                             'high_minus_low_model_advantage_gap':float(hi.mean()-lo.mean()),
                             'bootstrap95_high_minus_low_gap':np.quantile(contrast,[.025,.975]).tolist(),
                             'linear_novelty_slope_unadjusted':float(simple_slope),
                             'bootstrap95_linear_novelty_slope_unadjusted':np.quantile(boot_simple,[.025,.975]).tolist(),
                             'linear_novelty_slope_adjusted_for_taxon_richness':float(adjusted_slope),
                             'bootstrap95_linear_novelty_slope_adjusted_for_taxon_richness':np.quantile(boot_adjusted,[.025,.975]).tolist()}
    return out


if __name__=='__main__':
    out=summarize()
    (ROOT/'results/oral_pilot_assemblage_novelty.json').write_text(json.dumps(out,indent=2)+'\n')
    print(out['high_novelty_people'], out['low_or_equal_novelty_people'])
    for n,r in out['models'].items():print(n, r)
