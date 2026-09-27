"""Exact 5.0 run-to-analysis-to-sample metadata check for viewed gut candidate."""
from collections import Counter,defaultdict
from pathlib import Path
import hashlib,io,json,urllib.request
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];STUDY='MGYS00005154'
def get(url):
    with urllib.request.urlopen(url,timeout=35) as r:b=r.read()
    if len(b)>60_000_000:raise ValueError('oversized response')
    return b,{'url':url,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def paged(kind):
    url=f'https://www.ebi.ac.uk/metagenomics/api/v1/studies/{STUDY}/{kind}?page_size=1000'
    rows=[];refs=[];total=None;urls=set()
    while url:
        if len(refs)>=20 or url in urls:raise ValueError('pagination bound or loop')
        urls.add(url);b,r=get(url);d=json.loads(b);count=d['meta']['pagination']['count']
        if total is not None and count!=total:raise ValueError('pagination total changed')
        total=count;items=d['data'];rows.extend(items)
        r.update({'items':len(items),'declared_total':total});refs.append(r);url=d['links'].get('next')
    if len(rows)!=total or len({x['id'] for x in rows})!=total:raise ValueError('pagination incomplete or duplicated')
    return rows,refs
def run():
    m=pd.read_csv(ROOT/'data/raw/mgnify/manifest.csv').query('study==@STUDY')
    if len(m)!=1:raise ValueError('manifest identity')
    m=m.iloc[0];b,source=get(m.source_url)
    t=pd.read_csv(io.BytesIO(b),sep='\t',index_col=0).select_dtypes('number')
    genera=[(i.split(';g__')[1].split(';')[0] if ';g__' in i and i.split(';g__')[1].split(';')[0] else None) for i in t.index]
    t.index=genera;t=t[t.index.notnull()].groupby(level=0).sum()
    raw=set(t.columns);t=t.loc[:,t.sum(0)>0]
    if t.shape!=(int(m.n_genera),int(m.n_samples)):raise ValueError('manifest dimensions changed')
    x=t.T;x=x.loc[x.sum(1)>0];x=x.loc[:,(x>0).mean(0)>=.05];x=x.loc[x.sum(1)>0]
    if x.shape[1]>150:x=x[x.columns[np.argsort(-(x>0).mean(0).values)[:150]]];x=x.loc[x.sum(1)>0]
    if len(x)>400:x=x.sample(400,random_state=0)
    old=pd.read_csv(ROOT/'results/mgnify_audit_fdr.csv').query('study==@STUDY')
    if len(old)!=1 or len(x)!=int(old.iloc[0]['n']) or x.shape[1]!=int(old.iloc[0]['taxa']):raise ValueError('archive dimensions changed')
    analyses,ap=paged('analyses');samples,sp=paged('samples');byrun=defaultdict(list);byassembly=defaultdict(list)
    for a in analyses:
        for kind,index in (('run',byrun),('assembly',byassembly)):
            rel=a['relationships'].get(kind,{}).get('data')
            if rel:index[rel['id']].append(a)
    sample={z['id']:z for z in samples};retained=set(x.index)
    links=Counter(len(byrun[k]) for k in retained)
    selected=[a for k in x.index for a in byrun[k] if a['attributes'].get('pipeline-version')=='5.0']
    if len(selected)!=len(x):raise ValueError('no one-to-one 5.0 mapping')
    conflicts=sum(len({a['relationships']['sample']['data']['id'] for a in byrun[k]})>1 for k in retained)
    if conflicts:raise ValueError('cross-version sample conflict')
    linked=[]
    for a in selected:
        sid=a['relationships'].get('sample',{}).get('data',{}).get('id')
        if sid not in sample:raise ValueError('missing sample link')
        linked.append(sample[sid])
    desc=Counter(str(z['attributes'].get('sample-desc') or 'missing') for z in linked)
    site=Counter(v['value'] for z in linked for v in z['attributes'].get('sample-metadata',[]) if v['key'].lower() in ('body site','body_site','collection site'))
    hosts=Counter(v['value'] for z in linked for v in z['attributes'].get('sample-metadata',[]) if v['key'].lower()=='host scientific name' and v.get('value'))
    species=Counter(z['attributes'].get('species') or 'missing' for z in linked)
    return {'study':STUDY,'source':source,'api_pages':{'analyses':ap,'samples':sp},
            'raw_ssu_columns':len(raw),'nonzero_ssu_columns':t.shape[1],'retained_columns':len(x),'retained_taxa':x.shape[1],
            'analysis_count':len(analyses),'sample_count':len(samples),
            'exact_raw_run_matches':len(raw&byrun.keys()),'exact_retained_run_matches':len(retained&byrun.keys()),
            'exact_retained_assembly_matches':len(retained&byassembly.keys()),
            'current_analysis_versions_per_retained_run':dict(links),'cross_version_sample_link_conflicts':conflicts,
            'pipeline_5_0_selected_analysis_records':len(selected),'selected_analysis_type_counts':dict(Counter(a['attributes'].get('experiment-type') or 'missing' for a in selected)),
            'linked_sample_relationships':len(linked),'unique_linked_sample_ids':len({z['id'] for z in linked}),
            'linked_sample_descriptions':dict(desc),'linked_explicit_collection_site_values':dict(site),
            'linked_explicit_host_names':dict(hosts),'linked_normalized_species':dict(species),
            'scope':'exact 5.0 run-column matching on viewed study; descriptions and host are current metadata; independent people/families, historical method and rights unverified'}
if __name__=='__main__':
    d=run();(ROOT/'results/gut_candidate_column_identity.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
