"""Descriptive subject-level sensitivity for MDSINE2 Figure 3 source data.

The manuscript's per-(mouse,taxon) RMSE is clustered within mouse. This script
reports each mouse's median paired gap; 4/5 mice do not justify generalization.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from microtwin.mdsine_schedule import scheduled_days
from microtwin.popforecast import forecast


def summarize(cohort, all_timepoints=True):
    if cohort not in ('healthy', 'uc'):
        raise ValueError('cohort must be healthy or uc')
    base = Path(__file__).resolve().parents[1]
    source = pd.read_csv(base/f'data/raw/mdsine2_sourcedata/fig3_{cohort}_absolute.csv')
    raw = base/f'data/raw/mdsine2{"_uc" if cohort=="uc" else ""}'
    meta = pd.read_csv(raw/'metadata.tsv', sep='\t').set_index('sampleID')
    qpcr_ids = set(pd.read_csv(raw/'qpcr.tsv', sep='\t', index_col=0).index)
    count_ids = set(pd.read_csv(raw/'counts.tsv', sep='\t', index_col=0).columns)
    refs = source[source.Method == source.Method.iloc[0]]
    series = {}
    for subject, g in refs.groupby('HeldoutSubjectId'):
        m = meta[meta.subject.astype(str) == str(subject)]
        m = m[m.index.isin(qpcr_ids & count_ids)]
        days = scheduled_days(m.time.values, int(g.TimePoint.nunique()))
        for taxon, h in g.groupby('TaxonIdx'):
            h = h.sort_values('TimePoint')
            if h.TimePoint.tolist() != list(range(len(days))):
                raise ValueError('nonconsecutive or mismatched figure timepoints')
            series[(subject,taxon)] = (days, h.Truth.to_numpy())
    subjects = sorted(refs.HeldoutSubjectId.unique())
    rows=[]
    for (subject,taxon),(days,truth) in series.items():
        train=[series[(other,taxon)] for other in subjects if other!=subject]
        pred=forecast(train,days,truth[0],0,1e3,True)
        mask=np.ones(len(truth),dtype=bool) if all_timepoints else truth>1e-5
        if not mask.any():continue
        ours=np.sqrt(np.mean((pred[mask]-np.log10(truth[mask]+1e3))**2))
        rows.append((subject,taxon,ours))
    ours=pd.DataFrame(rows,columns=['subject','taxon','ours'])
    out={'cohort':cohort,'all_timepoints':all_timepoints,'n_subjects':len(subjects),
         'source':str(base/f'data/raw/mdsine2_sourcedata/fig3_{cohort}_absolute.csv'),
         'comparisons':{}}
    for method in ('MDSINE2 (No Modules)','RA-MDSINE2 (No Modules)','MDSINE2'):
        official=source[source.Method==method]
        if official.empty:continue
        def paired_rmse(x):
            truth = x.Truth.to_numpy()
            pred = x.Pred.to_numpy()
            mask = np.ones(len(x), bool) if all_timepoints else truth > 1e-5
            if not mask.any():
                return np.nan
            return float(np.sqrt(np.mean((np.log10(pred[mask]+1e3)-np.log10(truth[mask]+1e3))**2)))
        err=official.groupby(['HeldoutSubjectId','TaxonIdx']).apply(
            paired_rmse,include_groups=False).rename('official').reset_index()
        err.columns=['subject','taxon','official']
        merged=ours.merge(err,on=['subject','taxon'],validate='one_to_one').dropna()
        by_subject=[]
        for s,g in merged.groupby('subject'):
            by_subject.append({'subject':int(s),'taxon_pairs':int(len(g)),
                               'prior_median':float(g.ours.median()),'comparator_median':float(g.official.median()),
                               'median_paired_gap_prior_minus_comparator':float((g.ours-g.official).median()),
                               'mean_paired_gap_prior_minus_comparator':float((g.ours-g.official).mean())})
        out['comparisons'][method]={'subjects_prior_lower_median_gap':sum(r['median_paired_gap_prior_minus_comparator']<0 for r in by_subject),
                                    'per_subject':by_subject}
    return out


if __name__=='__main__':
    for co in ('healthy','uc'):
        for alltp in (False,True):
            value=summarize(co,alltp)
            out=Path(__file__).resolve().parents[1]/f'results/mdsine_subject_aggregate_{co}_{"all" if alltp else "detected"}.json'
            out.write_text(json.dumps(value,indent=2)+'\n')
            print(out, {m:v['subjects_prior_lower_median_gap'] for m,v in value['comparisons'].items()})
