"""Viewed MGnify oral-source exact run-column and collection-site mapping."""
import hashlib,io,json,urllib.request
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];STUDY='MGYS00002238'
def get(url):
    with urllib.request.urlopen(url,timeout=35) as r:b=r.read()
    if len(b)>60_000_000:raise ValueError('response too large')
    return b,{'url':url,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def run():
    m=pd.read_csv(ROOT/'data/raw/mgnify/manifest.csv').query('study==@STUDY')
    if len(m)!=1:raise ValueError('manifest identity')
    m=m.iloc[0];body,source=get(m.source_url)
    t=pd.read_csv(io.BytesIO(body),sep='\t',index_col=0).select_dtypes('number')
    genera=[(i.split(';g__')[1].split(';')[0] if ';g__' in i and i.split(';g__')[1].split(';')[0] else None) for i in t.index]
    t.index=genera;t=t[t.index.notnull()].groupby(level=0).sum()
    raw=set(t.columns);t=t.loc[:,t.sum(0)>0]
    if t.shape!=(int(m.n_genera),int(m.n_samples)):raise ValueError('manifest dimensions changed')
    x=t.T;x=x.loc[x.sum(1)>0];x=x.loc[:,(x>0).mean(0)>=.05];x=x.loc[x.sum(1)>0]
    if x.shape[1]>150:x=x[x.columns[np.argsort(-(x>0).mean(0).values)[:150]]];x=x.loc[x.sum(1)>0]
    if len(x)>400:x=x.sample(400,random_state=0)
    audit=pd.read_csv(ROOT/'results/mgnify_audit_fdr.csv').query('study==@STUDY')
    if len(audit)!=1 or len(x)!=int(audit.iloc[0]['n']) or x.shape[1]!=int(audit.iloc[0]['taxa']):raise ValueError('audit dimensions changed')
    records={};pages={};base=f'https://www.ebi.ac.uk/metagenomics/api/v1/studies/{STUDY}'
    for kind in ('analyses','samples'):
        b,ref=get(base+'/'+kind+'?page_size=1000');d=json.loads(b)
        if d['links']['next'] or len(d['data'])!=d['meta']['pagination']['count']:raise ValueError('incomplete pagination')
        records[kind]=d['data'];ref.update({'items':len(d['data']),'declared_total':d['meta']['pagination']['count']});pages[kind]=ref
    byrun=defaultdict(list);byassembly=defaultdict(list)
    for z in records['analyses']:
        for key,target in (('run',byrun),('assembly',byassembly)):
            rel=z['relationships'].get(key,{}).get('data')
            if rel:target[rel['id']].append(z)
    sample={z['id']:z for z in records['samples']}
    if len(sample)!=len(records['samples']):raise ValueError('duplicate sample ids')
    multiplicity=Counter(len(byrun[key]) for key in x.index if key in byrun)
    inconsistent_sample_links=sum(len({a['relationships']['sample']['data']['id'] for a in byrun[key]})>1 for key in x.index if key in byrun)
    matched=[a for key in x.index for a in byrun.get(key,[]) if a['attributes'].get('pipeline-version')=='5.0']
    if len(matched)!=len(x) or inconsistent_sample_links:raise ValueError('pipeline-5.0 match or cross-version sample link failed')
    linked=[];missing=0
    for a in matched:
        rel=a['relationships'].get('sample',{}).get('data')
        if not rel or rel['id'] not in sample:missing+=1;continue
        linked.append(sample[rel['id']])
    desc=Counter(str(z['attributes'].get('sample-desc') or 'missing') for z in linked)
    host=Counter(v['value'] for z in linked for v in z['attributes'].get('sample-metadata',[]) if v['key'].lower()=='host scientific name' and v.get('value'))
    species=Counter(z['attributes'].get('species') or 'missing' for z in linked)
    return {'study':STUDY,'source':source,'api_pages':pages,'raw_ssu_columns':len(raw),'nonzero_ssu_columns':t.shape[1],
            'retained_columns':len(x),'retained_taxa':x.shape[1],'analysis_count':len(records['analyses']),'sample_count':len(sample),
            'exact_raw_run_matches':len(raw&byrun.keys()),'exact_retained_run_matches':len(set(x.index)&byrun.keys()),
            'retained_selected_pipeline_5_0_analysis_records':len(matched),'analysis_versions_per_retained_run':dict(multiplicity),'inconsistent_sample_links_across_pipeline_versions':inconsistent_sample_links,'matched_analysis_type_counts':dict(Counter(a['attributes'].get('experiment-type') or 'missing' for a in matched)),
            'run_ids_with_multiple_current_analyses':sum(len(byrun[key])>1 for key in x.index if key in byrun),
            'exact_retained_assembly_matches':len(set(x.index)&byassembly.keys()),
            'linked_sample_relationships':len(linked),'unique_linked_sample_ids':len({z['id'] for z in linked}),
            'missing_sample_links':missing,'linked_sample_descriptions':dict(desc),
            'linked_explicit_host_names':dict(host),'linked_normalized_species':dict(species),
            'scope':'exact old run-column to matching pipeline-5.0 analysis and sample ID mapping; pipeline-4.1 analyses are second versions of same 111 runs, not extra samples; saliva/plaque sample descriptions; no participant independence, historical wet-lab certification, rights or fresh outcome test'}
if __name__=='__main__':
    d=run();(ROOT/'results/oral_column_identity.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
