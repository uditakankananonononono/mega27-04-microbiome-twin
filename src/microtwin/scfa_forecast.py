"""First-period, submitted-subject held-out SCFA development forecast.

No causal, clinical, independent-source or calibrated-coverage certificate.
"""
from __future__ import annotations
from datetime import datetime
from collections import Counter
import numpy as np
from sklearn.linear_model import Ridge

ANALYTES = ('2-Methylbutyric acid', 'Acetic acid', 'Butyric acid', 'Hexanoic acid',
            'Isobutyric acid', 'Isovaleric acid', 'Propionic acid', 'Valeric acid')


def _number(x):
    return type(x) in (int, float) and np.isfinite(x)


def prepare(metadata, assay):
    """Reject structural errors; count frozen metadata/assay exclusions privately."""
    samples = {}
    subjects = {}
    for row in metadata:
        name = row['sample_name']
        if not isinstance(name, str) or not name or name in samples:
            raise ValueError('missing or duplicate metadata sample label')
        samples[name] = row
        if str(row['Iteration']) != '1' or row['Timepoint'] not in ('T1', 'T2'):
            continue
        sid = row['Participant_ID']
        if not isinstance(sid, str) or not sid or sid != sid.strip():
            raise ValueError('invalid submitted subject label')
        group = row['Group']
        if group not in ('A', 'B'):
            raise ValueError('invalid group')
        block = subjects.setdefault(sid, {})
        if row['Timepoint'] in block:
            raise ValueError('duplicate first-period subject-time label')
        block[row['Timepoint']] = row
    cells = {}
    for row in assay:
        name, analyte = row['Client Sample ID'], row['Analyte']
        if name not in samples or analyte not in ANALYTES:
            raise ValueError('unmatched sample or analyte')
        if row['Unit'] != 'µg/g' or row['Client Matrix'] != 'Feces':
            raise ValueError('unsupported measurement unit or material')
        key = (name, analyte)
        if key in cells:
            raise ValueError('duplicate sample-analyte record')
        cells[key] = row
    if len(cells) != len(samples)*len(ANALYTES):
        raise ValueError('incomplete assay schema')
    ids, groups, baseline, target = [], [], [], []
    excluded = Counter()
    for sid in sorted(subjects):
        block = subjects[sid]
        if set(block) != {'T1', 'T2'}:
            excluded['missing_first_period_pair'] += 1; continue
        a, b = block['T1'], block['T2']
        if a['Group'] != b['Group']:
            raise ValueError('conflicting first-period group')
        dates = []
        for r in (a, b):
            value = r['collection_date']
            try:
                dates.append(value if isinstance(value, datetime) else datetime.fromisoformat(value))
            except (TypeError, ValueError):
                break
        if len(dates) != 2:
            excluded['unparsed_date'] += 1; continue
        if not 21 <= (dates[1]-dates[0]).days <= 35:
            excluded['outside_21_35_day_window'] += 1; continue
        pair, valid = [], True
        for r in (a, b):
            values = []
            for analyte in ANALYTES:
                cell = cells[(r['sample_name'], analyte)]
                val, lo, hi = cell['Results'], cell['LLOQ'], cell['ULOQ']
                comment = cell['Analysis Comments']
                if (not all(_number(x) for x in (val, lo, hi)) or val < 0 or not 0 < lo <= hi
                        or not lo <= val <= hi or comment not in (None, '')):
                    valid = False
                values.append(val)
            pair.append(values)
        if not valid:
            excluded['assay_complete_case_failure'] += 1; continue
        ids.append(sid); groups.append(a['Group']); baseline.append(pair[0]); target.append(pair[1])
    counts = dict(Counter(groups))
    report = {'candidate_subjects':len(subjects), 'eligible_subjects':len(ids),
              'eligible_arm_counts':counts, 'exclusions':dict(excluded),
              'evaluable':len(ids)>=40 and all(counts.get(g, 0)>=15 for g in ('A', 'B'))}
    return ids, np.array(groups), np.asarray(baseline, dtype=float), np.asarray(target, dtype=float), report


def folds(ids, groups):
    rng = np.random.default_rng(20261007)
    out = np.full(len(ids), -1, dtype=int)
    for group in ('A', 'B'):
        indices = np.array(sorted(np.flatnonzero(groups == group), key=lambda i:ids[i]))
        rng.shuffle(indices)
        out[indices] = np.arange(len(indices)) % 5
    if np.any(out < 0):
        raise ValueError('unknown split group')
    return out


def forecast_fold(x, y, groups, ids, train, test):
    """All transforms and donor selection are training-only."""
    if set(ids[i] for i in train) & set(ids[i] for i in test):
        raise ValueError('subject overlap')
    mu, sd = x[train].mean(axis=0), x[train].std(axis=0)
    sd = np.where(sd == 0, 1, sd)
    z = (x-mu)/sd
    arm = (groups=='B').astype(float)[:,None]
    features = np.concatenate((z, arm, z*arm), axis=1)
    delta = y[train]-x[train]
    model = Ridge(alpha=10, fit_intercept=True, solver='svd').fit(features[train], delta)
    result = {'ridge':np.maximum(0, x[test]+model.predict(features[test])),
              'persistence':x[test].copy(), 'arm_mean':[], 'nearest_three':[]}
    for i in test:
        donors = [j for j in train if groups[j]==groups[i]]
        if len(donors)<3:
            raise ValueError('insufficient same-arm training donors')
        nearest = sorted(donors, key=lambda j:(float(np.linalg.norm(z[j]-z[i])), ids[j]))[:3]
        result['arm_mean'].append(np.maximum(0, x[i]+(y[donors]-x[donors]).mean(axis=0)))
        result['nearest_three'].append(np.maximum(0, x[i]+(y[nearest]-x[nearest]).mean(axis=0)))
    return {k:np.asarray(v) for k,v in result.items()}, np.where(y[train].std(axis=0)==0,1,y[train].std(axis=0))


def evaluate(ids, groups, baseline, target):
    if len(set(ids))!=len(ids) or baseline.shape!=target.shape or baseline.shape!=(len(ids),8):
        raise ValueError('invalid independent-subject arrays')
    if not np.isfinite(baseline).all() or not np.isfinite(target).all() or np.any(baseline<0) or np.any(target<0):
        raise ValueError('invalid concentrations')
    x, y = np.log1p(baseline), np.log1p(target)
    assignment = folds(ids, groups)
    predictions = {k:np.full_like(y,np.nan) for k in ('ridge','persistence','arm_mean','nearest_three')}
    scales = np.full_like(y,np.nan)
    for fold in range(5):
        train, test = np.flatnonzero(assignment!=fold), np.flatnonzero(assignment==fold)
        p, sd = forecast_fold(x,y,groups,ids,train,test)
        replaced=y.copy(); replaced[test]=12345
        q,_=forecast_fold(x,replaced,groups,ids,train,test)
        if not all(np.array_equal(p[k],q[k]) for k in p):
            raise ValueError('target replacement invariance failed')
        scales[test]=sd
        for k in p:predictions[k][test]=p[k]
    if not all(np.isfinite(p).all() for p in predictions.values()):
        raise ValueError('nonfinite or unscored forecast')
    errors={k:np.mean(np.abs(p-y)/scales,axis=1) for k,p in predictions.items()}
    summary={k:{'primary_mean_error':float(e.mean()),
                'unscaled_mean_absolute_log_error':float(np.abs(predictions[k]-y).mean()),
                'per_analyte_mean_absolute_log_error':np.abs(predictions[k]-y).mean(axis=0).tolist()}
             for k,e in errors.items()}
    rng=np.random.default_rng(20261007); draws=rng.integers(0,len(ids),(2000,len(ids)))
    comparisons={}
    for k in ('persistence','arm_mean','nearest_three'):
        diff=errors['ridge']-errors[k]; ci=np.quantile(diff[draws].mean(axis=1),[.025,.975])
        comparisons[k]={'paired_mean_difference':float(diff.mean()),'bootstrap_95_percent_interval':ci.tolist(),
                        'relative_error_reduction':float(1-errors['ridge'].mean()/errors[k].mean()) if errors[k].mean()>0 else None}
    win=all(c['relative_error_reduction'] is not None and c['relative_error_reduction']>=.1
            and c['bootstrap_95_percent_interval'][1]<0 for c in comparisons.values())
    return {'subjects_scored':len(ids),'fold_sizes':dict(Counter(int(x) for x in assignment)),
            'analytes':list(ANALYTES),'models':summary,'comparisons':comparisons,'useful_win':win,
            'target_replacement_invariance':True,'all_predictions_finite':True,
            'scope':'same-study first-period SCFA development forecast; no causal, clinical, independent-source or calibration certificate'}
