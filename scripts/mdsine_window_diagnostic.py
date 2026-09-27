"""Within-viewed-mouse intervention-window diagnostic, protocol in results/PREREG_20260927_mdsine_window_diagnostic.md."""
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
WINDOWS=[('pre',-np.inf,21.5,False),('diet',21.5,28.5,True),('between_diet_vanco',28.5,35.5,False),('vancomycin',35.5,42.5,True),('between_vanco_gent',42.5,50.5,False),('gentamicin',50.5,57.5,True),('after_gent',57.5,np.inf,False)]

def _window(t):
    for name,a,b,inclusive in WINDOWS:
        if (a<=t<=b if inclusive else a<t<b): return name
    raise ValueError(f'unassigned day {t}')

def run(cohort):
    raw=ROOT/('data/raw/mdsine2' if cohort=='healthy' else 'data/raw/mdsine2_uc')
    perturb=pd.read_csv(raw/'perturbations.tsv',sep='\t')
    assert set(perturb.name)=={'High Fat Diet','Vancomycin','Gentamicin'}
    assert {(r['name'],float(r['start']),float(r['end'])) for _,r in perturb.iterrows()}=={('High Fat Diet',21.5,28.5),('Vancomycin',35.5,42.5),('Gentamicin',50.5,57.5)}
    d=pd.read_csv(ROOT/f'data/raw/mdsine2_sourcedata/fig3_{cohort}_absolute.csv')
    meta=pd.read_csv(raw/'metadata.tsv',sep='\t').set_index('sampleID')
    qpcr=pd.read_csv(raw/'qpcr.tsv',sep='\t',index_col=0)
    counts=pd.read_csv(raw/'counts.tsv',sep='\t',index_col=0)
    model=d[d.Method=='MDSINE2 (No Modules)'].copy()
    if model.empty:raise ValueError('comparator absent')
    schedule={}
    for s,g in model.groupby('HeldoutSubjectId'):
        m=meta[meta.subject.astype(str)==str(s)]
        m=m[m.index.isin(qpcr.index)&m.index.isin(counts.columns)].sort_values('time')
        schedule[s]=scheduled_days(m.time.values,int(g.TimePoint.nunique()))
    model['day']=[schedule[s][int(k)] for s,k in zip(model.HeldoutSubjectId,model.TimePoint)]
    keys=['HeldoutSubjectId','TaxonIdx']
    groups={k:g.sort_values('day') for k,g in model.groupby(keys)}
    subjects=sorted(model.HeldoutSubjectId.unique());taxa=sorted(model.TaxonIdx.unique())
    entries=[]; full={"detected":{"ours":[],"other":[]},"all":{"ours":[],"other":[]}}
    for s in subjects:
        for j in taxa:
            g=groups[(s,j)]
            day=g.day.to_numpy(); tr=g.Truth.to_numpy()
            prediction=forecast([(groups[(o,j)].day.to_numpy(),groups[(o,j)].Truth.to_numpy()) for o in subjects if o!=s],day,tr[0],0,EPS,True)
            assert len(prediction)==len(g)
            for endpoint in ['detected','all']:
                selected=(tr>LB) if endpoint=='detected' else np.ones(len(tr),bool)
                if not selected.any():continue
                y=np.log10(tr[selected]+EPS)
                full[endpoint]['ours'].append(float(np.sqrt(np.mean((prediction[selected]-y)**2))))
                full[endpoint]['other'].append(float(np.sqrt(np.mean((np.log10(g.Pred.to_numpy()[selected]+EPS)-y)**2))))
            for name in [w[0] for w in WINDOWS]:
                mask=np.array([_window(t)==name for t in day])
                for endpoint in ['detected','all']:
                    selected=mask & ((tr>LB) if endpoint=='detected' else np.ones(len(tr),bool))
                    if not selected.any():continue
                    y=np.log10(tr[selected]+EPS)
                    ours=float(np.sqrt(np.mean((prediction[selected]-y)**2)))
                    other=float(np.sqrt(np.mean((np.log10(g.Pred.to_numpy()[selected]+EPS)-y)**2)))
                    entries.append({'subject':int(s),'taxon':int(j),'window':name,'endpoint':endpoint,'n_timepoints':int(selected.sum()),'gap':ours-other})
    a=pd.DataFrame(entries); out=[]
    for (endpoint,name),g in a.groupby(['endpoint','window']):
        mouse=g.groupby('subject').gap.median()
        out.append({'endpoint':endpoint,'window':name,'n_mice':int(mouse.size),'n_mouse_taxon_pairs':int(len(g)),
                    'scored_timepoints':int(g.n_timepoints.sum()),'mean_mouse_median_gap':float(mouse.mean()),
                    'negative_mouse_gaps':int((mouse<0).sum()),'mouse_median_gaps':[float(v) for v in mouse.values]})
    order={w[0]:i for i,w in enumerate(WINDOWS)}
    out.sort(key=lambda r:(r['endpoint'],order[r['window']]))
    full_summary={endpoint:{m:{'median':float(np.median(vals)),'n':len(vals)} for m,vals in models.items()} for endpoint,models in full.items()}
    for endpoint,models in full_summary.items():
        archive=json.load(open(ROOT/f"results/mdsine2_headtohead_{cohort}{'_alltimepoints' if endpoint=='all' else ''}.json"))
        for m,key in [('ours','PresenceConditionalPopulation (ours)'),('other','MDSINE2 (No Modules)')]:
            assert models[m]['n']==archive[key]['n'] and np.isclose(models[m]['median'],archive[key]['median'],atol=1e-10),f'full-period mismatch: {cohort} {endpoint} {m}'
    return {'cohort':cohort,'subjects':len(subjects),'taxa':len(taxa),'comparator':'MDSINE2 (No Modules)',
            'full_period_reproduction':full_summary,'windows':out,'scope':'viewed cohorts; descriptive, noncausal and not external validation'}

if __name__=='__main__':
    for cohort in ['healthy','uc']:
        result=run(cohort)
        (ROOT/f'results/mdsine_window_{cohort}.json').write_text(json.dumps(result,indent=2)+'\n')
        print(cohort,[(w['endpoint'],w['window'],round(w['mean_mouse_median_gap'],3),w['negative_mouse_gaps'],w['n_mice']) for w in result['windows']])
