"""Locked exploratory name-label stratification of the old MGnify audit."""
import json
from pathlib import Path
import pandas as pd
from microtwin.eligibility import ASSEMBLY
ROOT=Path(__file__).resolve().parents[1]

def run(manifest=None,audit=None):
    m=pd.read_csv(manifest or ROOT/'data/raw/mgnify/manifest.csv',dtype={'study':str})
    a=pd.read_csv(audit or ROOT/'results/mgnify_audit_fdr.csv',dtype={'study':str})
    for name,d in [('manifest',m),('audit',a)]:
        if d.study.isna().any() or d.study.duplicated().any():
            raise ValueError(f'{name}: missing or duplicate study IDs')
    if set(m.study)!=set(a.study):raise ValueError('manifest and audit study IDs differ')
    if len(m)!=160:raise ValueError('expected frozen 160-study archive')
    d=a.merge(m[['study','study_name']],on='study',validate='one_to_one')
    d['assembly_name_flag']=d.study_name.fillna('').map(lambda x:bool(ASSEMBLY.search(x)))
    if (d.median_prior<0).any():raise ValueError('negative prior median')
    d['relative_gain']=(d.median_prior-d.median_interaction)/d.median_prior.where(d.median_prior>0)
    def summarize(g):
        wins=int(g.int_wins.sum());prior=int(g.prior_wins.sum())
        return {'tables':int(len(g)),'original_160_BH_interaction_wins':wins,
                'original_160_BH_prior_wins':prior,'neither':int(len(g)-wins-prior),
                'median_relative_gain':float(g.relative_gain.median()),
                'undefined_relative_gain_tables':int(g.relative_gain.isna().sum()),
                'median_absolute_gain':float(g.gain.median())}
    groups={('assembly_indicated' if flag else 'unflagged_unknown_assay'):summarize(g)
            for flag,g in d.groupby('assembly_name_flag')}
    biome=[]
    for (label,flag),g in d.groupby(['biome_short','assembly_name_flag']):
        biome.append({'biome':str(label),'assay_label':'assembly_indicated' if flag else 'unflagged_unknown_assay',**summarize(g)})
    result={'basis':'160 previously viewed MGnify study tables; study-name assembly indication only; original 160-table BH q-values',
            'all':summarize(d),'strata':groups,'by_biome':biome,
            'limits':'Unflagged is not certified amplicon; no new BH tests, inferential assay effect, independent source-family count or untouched external benchmark.'}
    assert sum(x['tables'] for x in groups.values())==160
    assert sum(x['original_160_BH_interaction_wins'] for x in groups.values())==121
    assert sum(x['original_160_BH_prior_wins'] for x in groups.values())==6
    return result
if __name__=='__main__':
    result=run();(ROOT/'results/mgnify_assay_descriptive.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'all':result['all'],'strata':result['strata'],'digestive':[x for x in result['by_biome'] if x['biome']=='Digestive system']},indent=2))
