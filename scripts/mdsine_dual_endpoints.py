"""Exploratory detection/abundance decomposition; protocol results/PREREG_20260927_mdsine_dual_endpoints.md."""
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from microtwin.popforecast import forecast
from microtwin.mdsine_schedule import scheduled_days
EPS=1e3; LB=1e-5

def run(cohort):
    raw=ROOT/('data/raw/mdsine2' if cohort=='healthy' else 'data/raw/mdsine2_uc')
    d=pd.read_csv(ROOT/f'data/raw/mdsine2_sourcedata/fig3_{cohort}_absolute.csv')
    model=d[d.Method=='MDSINE2 (No Modules)'].copy()
    meta=pd.read_csv(raw/'metadata.tsv',sep='\t').set_index('sampleID')
    qpcr=pd.read_csv(raw/'qpcr.tsv',sep='\t',index_col=0)
    counts=pd.read_csv(raw/'counts.tsv',sep='\t',index_col=0)
    schedule={}
    for s,g in model.groupby('HeldoutSubjectId'):
        m=meta[meta.subject.astype(str)==str(s)]
        m=m[m.index.isin(qpcr.index)&m.index.isin(counts.columns)].sort_values('time')
        schedule[s]=scheduled_days(m.time.values,int(g.TimePoint.nunique()))
    model['day']=[schedule[s][int(k)] for s,k in zip(model.HeldoutSubjectId,model.TimePoint)]
    groups={k:g.sort_values('day') for k,g in model.groupby(['HeldoutSubjectId','TaxonIdx'])}
    subs=sorted(model.HeldoutSubjectId.unique()); taxa=sorted(model.TaxonIdx.unique())
    stats={m:{'tp':0,'tn':0,'fp':0,'fn':0,'mouse':{},'pair_errors':[]} for m in ['population baseline','MDSINE2 no modules']}
    for s in subs:
        for j in taxa:
            g=groups[(s,j)];dy=g.day.to_numpy();tr=g.Truth.to_numpy()
            logged=forecast([(groups[(o,j)].day.to_numpy(),groups[(o,j)].Truth.to_numpy()) for o in subs if o!=s],dy,tr[0],0,EPS,True)
            pred={'population baseline':np.maximum(10**logged-EPS,0),'MDSINE2 no modules':g.Pred.to_numpy()}
            actual=tr>LB
            for name,p in pred.items():
                seen=p>LB; v=stats[name]
                v['tp']+=int(np.sum(seen&actual));v['tn']+=int(np.sum(~seen&~actual));v['fp']+=int(np.sum(seen&~actual));v['fn']+=int(np.sum(~seen&actual))
                if actual.any():
                    error=float(np.sqrt(np.mean((np.log10(p[actual]+EPS)-np.log10(tr[actual]+EPS))**2)))
                    v['mouse'].setdefault(int(s),[]).append(error)
                    v['pair_errors'].append(error)
    result={}
    for name,v in stats.items():
        n=sum(v[k] for k in ['tp','tn','fp','fn'])
        conditional={int(s):float(np.median(errors)) for s,errors in v['mouse'].items()}
        pair_median=float(np.median(v['pair_errors']))
        result[name]={k:v[k] for k in ['tp','tn','fp','fn']}
        result[name].update({'n_timepoints':n,'sensitivity':v['tp']/(v['tp']+v['fn']) if v['tp']+v['fn'] else None,
            'specificity':v['tn']/(v['tn']+v['fp']) if v['tn']+v['fp'] else None,
            'balanced_accuracy':0.5*(v['tp']/(v['tp']+v['fn'])+v['tn']/(v['tn']+v['fp'])) if v['tp']+v['fn'] and v['tn']+v['fp'] else None,
            'positive_prediction_rate':(v['tp']+v['fp'])/n,'pair_median_conditional_rmse':pair_median,'pair_count':len(v['pair_errors']),
            'mean_mouse_median_conditional_rmse':float(np.mean(list(conditional.values()))),
            'mouse_median_conditional_rmse':{str(k):v for k,v in conditional.items()}})
    # The conditional per-pair metric must reproduce the archived official medians.
    archive=json.load(open(ROOT/f'results/mdsine2_headtohead_{cohort}.json'))
    for name,key in [('population baseline','PresenceConditionalPopulation (ours)'),('MDSINE2 no modules','MDSINE2 (No Modules)')]:
        assert set(map(int,result[name]['mouse_median_conditional_rmse']))==set(subs)
        assert result[name]['pair_count']==archive[key]['n'] and np.isclose(result[name]['pair_median_conditional_rmse'],archive[key]['median'],atol=1e-10)
    return {'cohort':cohort,'mouse_count':len(subs),'taxa_count':len(taxa),'threshold':LB,'epsilon':EPS,
            'methods':result,'archived_pair_medians':{x:archive[y]['median'] for x,y in [('population baseline','PresenceConditionalPopulation (ours)'),('MDSINE2 no modules','MDSINE2 (No Modules)')]},
            'scope':'viewed-cohort exploratory metric decomposition, no external validation'}

if __name__=='__main__':
    for cohort in ['healthy','uc']:
        x=run(cohort)
        (ROOT/f'results/mdsine_dual_{cohort}.json').write_text(json.dumps(x,indent=2)+'\n')
        print(cohort,{m:{k:round(v,4) if isinstance(v,float) else v for k,v in d.items() if k not in ['mouse_median_conditional_rmse']} for m,d in x['methods'].items()})
