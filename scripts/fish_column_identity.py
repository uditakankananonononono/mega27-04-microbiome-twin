"""Exact archived SSU assembly-column linkage, no raw rows retained."""
from pathlib import Path
from collections import Counter
import hashlib,io,json,urllib.request
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
STUDY='MGYS00006086'
BASE=f'https://www.ebi.ac.uk/metagenomics/api/v1/studies/{STUDY}'
def fetch(url):
    with urllib.request.urlopen(url,timeout=35) as response:
        body=response.read()
    if len(body)>60_000_000:raise ValueError('bounded response exceeded')
    return body,{'url':url,'response_sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body)}
def run():
    manifest=pd.read_csv(ROOT/'data/raw/mgnify/manifest.csv').query('study==@STUDY')
    if len(manifest)!=1:raise ValueError('manifest identity not unique')
    m=manifest.iloc[0];source,source_ref=fetch(m.source_url)
    t=pd.read_csv(io.BytesIO(source),sep='\t',index_col=0).select_dtypes('number')
    genera=[(i.split(';g__')[1].split(';')[0] if ';g__' in i and i.split(';g__')[1].split(';')[0] else None) for i in t.index]
    t.index=genera;t=t[t.index.notnull()].groupby(level=0).sum()
    raw_columns=list(t.columns)
    t=t.loc[:,t.sum(0)>0]
    x=t.T;x=x.loc[x.sum(1)>0];x=x.loc[:,(x>0).mean(0)>=.05];x=x.loc[x.sum(1)>0]
    if x.shape[1]>150:x=x[x.columns[(-((x>0).mean(0))).argsort()[:150]]];x=x.loc[x.sum(1)>0]
    if len(x)>400:x=x.sample(400,random_state=0)
    if (len(raw_columns),t.shape[1],len(x),x.shape[1])!=(150,142,135,3):raise ValueError('source or screen dimensions changed')
    pages={};d={}
    for kind in ('analyses','samples'):
        url=BASE+'/'+kind+'?page_size=1000';body,ref=fetch(url)
        obj=json.loads(body);records=obj['data'];total=obj['meta']['pagination']['count']
        if obj['links']['next'] or len(records)!=total or len(records)>250:raise ValueError('source pagination incomplete')
        ref.update({'items':len(records),'declared_total':total});pages[kind]=[ref];d[kind]=records
    a=d['analyses'];s=d['samples']
    keys=[]
    for z in a:
        rel=z['relationships'].get('assembly',{}).get('data')
        if rel:keys.append((rel['id'],z))
    by_assembly={}
    for k,z in keys:
        if k in by_assembly:raise ValueError('nonunique assembly to analysis link')
        by_assembly[k]=z
    raw=set(raw_columns);positive=set(t.columns);retained=set(x.index)
    if len(raw)!=len(raw_columns):raise ValueError('duplicate source columns')
    sample_by_id={z['id']:z for z in s}
    if len(sample_by_id)!=len(s):raise ValueError('duplicate sample IDs')
    retained_analyses=[by_assembly[z] for z in retained if z in by_assembly]
    linked_samples=[]
    for z in retained_analyses:
        rel=z['relationships'].get('sample',{}).get('data')
        if rel and rel['id'] in sample_by_id:linked_samples.append(sample_by_id[rel['id']])
    host=Counter();species=Counter()
    for z in linked_samples:
        host.update(v['value'] for v in z['attributes'].get('sample-metadata',[]) if v['key'].lower()=='host scientific name' and v.get('value'))
        species.update([z['attributes'].get('species') or 'missing'])
    return {'study':STUDY,'source':source_ref,'api_pages':pages,
            'raw_ssu_columns':len(raw),'nonzero_ssu_columns':len(positive),'retained_audit_columns':len(retained),
            'analysis_count':len(a),'sample_count':len(s),'assembly_relationships':len(keys),
            'exact_assembly_matches_raw':len(raw & by_assembly.keys()),
            'exact_assembly_matches_positive':len(positive & by_assembly.keys()),
            'exact_assembly_matches_retained':len(retained & by_assembly.keys()),
            'unmatched_retained':len(retained-by_assembly.keys()),
            'matched_retained_analysis_types':dict(Counter(z['attributes'].get('experiment-type') or 'missing' for z in retained_analyses)),
            'linked_retained_samples':len(linked_samples),
            'unique_linked_retained_samples':len({z['id'] for z in linked_samples}),
            'linked_sample_host_names':dict(host),'linked_sample_normalized_species':dict(species),
            'scope':'exact current MGnify assembly-to-analysis-to-sample metadata linkage for viewed fish source; historical assay method, independent biological family and rights not certified; old 160 BH unchanged'}
if __name__=='__main__':
    obj=run();(ROOT/'results/fish_column_identity.json').write_text(json.dumps(obj,indent=2)+'\n');print(json.dumps(obj,indent=2))
