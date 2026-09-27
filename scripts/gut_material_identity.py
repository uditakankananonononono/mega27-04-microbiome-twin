"""Post-inspection source-material check, locked by dated amendment."""
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import hashlib, io, urllib.request
import numpy as np
import pandas as pd
import json
from pathlib import Path
from scripts import gut_candidate_column_identity as exact
from scripts.gut_candidate_column_identity import ROOT, STUDY, paged

KEYS=('environment (material)','environment (feature)','environment (biome)','host scientific name')
def summarize_material(linked,expected=400):
    if len(linked)!=expected or len({s['id'] for s in linked})!=expected:
        raise ValueError('linked-sample cardinality changed')
    out={}
    for key in KEYS:
        c=Counter()
        for sample in linked:
            values=[str(v.get('value') or '').strip() for v in sample['attributes'].get('sample-metadata',[])
                    if str(v.get('key') or '').strip().lower()==key]
            # Multiple values per key cannot be silently collapsed into a passing aggregate.
            if len(values)!=1 or not values[0]:
                c['missing_or_ambiguous']+=1
            else:c[values[0]]+=1
        out[key]=dict(c)
    return out

def run():
    previous=json.loads((ROOT/'results/gut_candidate_column_identity.json').read_text())
    urls=[previous['source']['url']]+[p['url'] for kind in ('analyses','samples') for p in previous['api_pages'][kind]]
    # Bounded concurrent transfer; the live pagination walker below checks actual next links.
    def load(url):
        with urllib.request.urlopen(url,timeout=35) as r: body=r.read()
        if len(body)>60_000_000:raise ValueError('oversized source response')
        return url,body
    with ThreadPoolExecutor(max_workers=7) as pool:cached=dict(pool.map(load,urls))
    def cached_get(url):
        if url not in cached:raise ValueError('new pagination URL not in frozen source list')
        body=cached[url]
        return body,{'url':url,'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body)}
    original_get=exact.get
    exact.get=cached_get
    try:
        current=exact.run() # replays archived taxonomy aggregation, old caps, and exact run links
        analyses,ap=paged('analyses'); samples,sp=paged('samples')
    finally:exact.get=original_get
    for key in ('retained_columns','unique_linked_sample_ids','retained_taxa','exact_retained_run_matches'):
        if current[key]!=previous[key]:raise ValueError(f'archive identity changed: {key}')
    if [(x['url'],x['items'],x['declared_total']) for x in sp] != [(x['url'],x['items'],x['declared_total']) for x in previous['api_pages']['samples']]:
        raise ValueError('sample pagination changed')
    if [(x['url'],x['items'],x['declared_total']) for x in ap] != [(x['url'],x['items'],x['declared_total']) for x in previous['api_pages']['analyses']]:
        raise ValueError('analysis pagination changed')
    # Recreate the retained set from the actual current SSU source, not a remembered ID list.
    t=pd.read_csv(io.BytesIO(cached[current['source']['url']]),sep='\t',index_col=0).select_dtypes('number')
    genera=[(i.split(';g__')[1].split(';')[0] if ';g__' in i and i.split(';g__')[1].split(';')[0] else None) for i in t.index]
    t.index=genera;t=t[t.index.notnull()].groupby(level=0).sum();t=t.loc[:,t.sum(0)>0]
    x=t.T;x=x.loc[x.sum(1)>0];x=x.loc[:,(x>0).mean(0)>=.05];x=x.loc[x.sum(1)>0]
    if x.shape[1]>150:x=x[x.columns[np.argsort(-(x>0).mean(0).values)[:150]]];x=x.loc[x.sum(1)>0]
    if len(x)>400:x=x.sample(400,random_state=0)
    retained=set(x.index)
    if len(retained)!=400 or x.shape[1]!=150:raise ValueError('retained source dimensions changed')
    byrun=defaultdict(list)
    for a in analyses:
        run=a['relationships'].get('run',{}).get('data')
        if run and a['attributes'].get('pipeline-version')=='5.0':byrun[run['id']].append(a)
    sample_by_id={z['id']:z for z in samples}
    linked=[]
    for run in retained:
        if len(byrun[run])!=1:raise ValueError('retained run needs one 5.0 analysis')
        sid=byrun[run][0]['relationships'].get('sample',{}).get('data',{}).get('id')
        if sid not in sample_by_id:raise ValueError('missing linked sample')
        linked.append(sample_by_id[sid])
    fields=summarize_material(linked,expected=400)
    if fields['environment (material)']!={'ENVO:feces':400}:
        raise ValueError('not every retained linked sample has a feces material annotation')
    all_fields=summarize_material(samples,expected=529)
    return {'study':STUDY,'amendment':'results/PREREG_20260927_feces_material_amendment.md',
            'source':current['source'],'api_pages':{'analyses':ap,'samples':sp},
            'all_source_samples':len(samples),'sample_page_1_byte_hash_changed':sp[0]['sha256']!=previous['api_pages']['samples'][0]['sha256'],
            'exact_mapped_retained_run_columns':len(retained),'unique_retained_linked_samples':len({s['id'] for s in linked}),
            'linked_retained_sample_metadata':fields,'all_source_sample_metadata':all_fields,
            'canonical_linked_sample_fingerprint_sha256':hashlib.sha256('\n'.join(sorted(s['id'] for s in linked)).encode()).hexdigest(),
            'site_metadata_compatible':True,
            'scope':'post-inspection source-annotation feces compatibility on current exact 400 linked run samples; no independent specimen verification, person/family lineage, historical assay, rights or untouched benchmark'}
if __name__=='__main__':
    result=run();(ROOT/'results/gut_material_identity.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
