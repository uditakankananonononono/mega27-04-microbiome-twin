"""Exact SSU run-column to current analysis and sample host-conflict linkage."""
import hashlib,io,json,urllib.request
from collections import Counter
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];STUDY='MGYS00006755'
def get(url):
    with urllib.request.urlopen(url,timeout=35) as r:b=r.read()
    if len(b)>60_000_000:raise ValueError('response too large')
    return b,{'url':url,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def run():
    m=pd.read_csv(ROOT/'data/raw/mgnify/manifest.csv').query('study==@STUDY')
    if len(m)!=1:raise ValueError('manifest identity')
    m=m.iloc[0];b,source=get(m.source_url)
    t=pd.read_csv(io.BytesIO(b),sep='\t',index_col=0).select_dtypes('number')
    genera=[(i.split(';g__')[1].split(';')[0] if ';g__' in i and i.split(';g__')[1].split(';')[0] else None) for i in t.index]
    t.index=genera;t=t[t.index.notnull()].groupby(level=0).sum()
    raw_ids=set(t.columns);t=t.loc[:,t.sum(0)>0]
    if t.shape!=(int(m.n_genera),int(m.n_samples)):raise ValueError('source/manifest dimensions')
    x=t.T;x=x.loc[x.sum(1)>0];x=x.loc[:,(x>0).mean(0)>=.05];x=x.loc[x.sum(1)>0]
    if x.shape[1]>150:x=x[x.columns[np.argsort(-(x>0).mean(0).values)[:150]]];x=x.loc[x.sum(1)>0]
    if len(x)>400:x=x.sample(400,random_state=0)
    old=pd.read_csv(ROOT/'results/mgnify_audit_fdr.csv').query('study==@STUDY')
    if len(old)!=1 or len(x)!=int(old.iloc[0]['n']) or x.shape[1]!=int(old.iloc[0]['taxa']):raise ValueError('archived audit dimensions')
    records={};pages={};base=f'https://www.ebi.ac.uk/metagenomics/api/v1/studies/{STUDY}'
    for kind in ('analyses','samples'):
        b,p=get(base+'/'+kind+'?page_size=1000');d=json.loads(b)
        if d['links']['next'] or len(d['data'])!=d['meta']['pagination']['count']:raise ValueError('incomplete pagination')
        p.update({'count':len(d['data']),'declared_total':d['meta']['pagination']['count']});pages[kind]=p;records[kind]=d['data']
    a=records['analyses'];s={z['id']:z for z in records['samples']}
    byrun={};byassembly={}
    for z in a:
        for rel,index in (('run',byrun),('assembly',byassembly)):
            obj=z['relationships'].get(rel,{}).get('data')
            if obj:
                if obj['id'] in index:raise ValueError('nonunique source relationship')
                index[obj['id']]=z
    retained=set(x.index)
    matches=[byrun[v] for v in retained if v in byrun]
    sample_ids=[];host=Counter();species=Counter();conflicts=0;missing=0
    for z in matches:
        rel=z['relationships'].get('sample',{}).get('data')
        if not rel or rel['id'] not in s:missing+=1;continue
        sample=s[rel['id']];sample_ids.append(rel['id'])
        names=[v['value'] for v in sample['attributes'].get('sample-metadata',[]) if v['key'].lower()=='host scientific name' and v.get('value')]
        host.update(names);species.update([sample['attributes'].get('species') or 'missing'])
        if sample['attributes'].get('species')=='Homo sapiens' and names and all(v.lower() not in ('human','homo sapiens') for v in names):conflicts+=1
    return {'study':STUDY,'source':source,'api_pages':pages,'raw_columns':len(raw_ids),'nonzero_columns':t.shape[1],'retained_columns':len(retained),'retained_taxa':x.shape[1],
            'analysis_count':len(a),'sample_count':len(s),'exact_run_matches_raw':len(raw_ids & byrun.keys()),'exact_run_matches_retained':len(retained & byrun.keys()),
            'exact_assembly_matches_retained':len(retained & byassembly.keys()),'exact_sample_id_matches_retained':len(retained & s.keys()),
            'matched_retained_analysis_types':dict(Counter(z['attributes'].get('experiment-type') or 'missing' for z in matches)),
            'linked_retained_samples':len(sample_ids),'unique_linked_retained_samples':len(set(sample_ids)),'unlinked_retained_matches':missing,
            'linked_retained_explicit_host_name_counts':dict(host),'linked_retained_normalized_species_counts':dict(species),
            'linked_retained_explicit_nonhuman_vs_normalized_human_conflicts':conflicts,
            'scope':'exact current run-to-analysis-to-sample ID mapping; metadata conflict not adjudicated; original BH unchanged; viewed source only'}
if __name__=='__main__':
    d=run();(ROOT/'results/conflicted_host_column_identity.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
