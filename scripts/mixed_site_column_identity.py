"""Exact SSU run columns and structured site ontology mismatch on viewed source."""
import hashlib,io,json,urllib.request
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];STUDY='MGYS00006794'
def get(url):
    with urllib.request.urlopen(url,timeout=35) as r:b=r.read()
    if len(b)>60_000_000:raise ValueError('oversized response')
    return b,{'url':url,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def ontology(obo_id,name):
    url=f'https://www.ebi.ac.uk/ols4/api/ontologies/{name}/terms?obo_id={obo_id}'
    b,r=get(url);entries=json.loads(b).get('_embedded',{}).get('terms',[])
    hits=[x for x in entries if x.get('obo_id')==obo_id]
    if len(hits)!=1:raise ValueError('ontology resolution nonunique')
    r.update({'obo_id':obo_id,'label':hits[0]['label']});return r
def run():
    m=pd.read_csv(ROOT/'data/raw/mgnify/manifest.csv').query('study==@STUDY')
    if len(m)!=1:raise ValueError('manifest identity')
    m=m.iloc[0];b,source=get(m.source_url)
    t=pd.read_csv(io.BytesIO(b),sep='\t',index_col=0).select_dtypes('number')
    taxa=[(i.split(';g__')[1].split(';')[0] if ';g__' in i and i.split(';g__')[1].split(';')[0] else None) for i in t.index]
    t.index=taxa;t=t[t.index.notnull()].groupby(level=0).sum()
    raw=set(t.columns);t=t.loc[:,t.sum(0)>0]
    if t.shape!=(int(m.n_genera),int(m.n_samples)):raise ValueError('manifest dimensions changed')
    x=t.T;x=x.loc[x.sum(1)>0];x=x.loc[:,(x>0).mean(0)>=.05];x=x.loc[x.sum(1)>0]
    if x.shape[1]>150:x=x[x.columns[np.argsort(-(x>0).mean(0).values)[:150]]];x=x.loc[x.sum(1)>0]
    if len(x)>400:x=x.sample(400,random_state=0)
    old=pd.read_csv(ROOT/'results/mgnify_audit_fdr.csv').query('study==@STUDY')
    if len(old)!=1 or len(x)!=int(old.iloc[0]['n']) or x.shape[1]!=int(old.iloc[0]['taxa']):raise ValueError('audit dimensions changed')
    pages={};records={}
    for kind in ('analyses','samples'):
        b,r=get(f'https://www.ebi.ac.uk/metagenomics/api/v1/studies/{STUDY}/{kind}?page_size=1000');d=json.loads(b)
        if d['links']['next'] or len(d['data'])!=d['meta']['pagination']['count']:raise ValueError('incomplete source pagination')
        r.update({'items':len(d['data']),'declared_total':d['meta']['pagination']['count']});pages[kind]=r;records[kind]=d['data']
    byrun=defaultdict(list);byassembly=defaultdict(list)
    for a in records['analyses']:
        for kind,index in (('run',byrun),('assembly',byassembly)):
            rel=a['relationships'].get(kind,{}).get('data')
            if rel:index[rel['id']].append(a)
    selected=[a for k in x.index for a in byrun[k] if a['attributes'].get('pipeline-version')=='5.0']
    if len(selected)!=len(x):raise ValueError('no one-to-one source pipeline mapping')
    samples={z['id']:z for z in records['samples']};linked=[]
    for a in selected:
        rel=a['relationships'].get('sample',{}).get('data')
        if not rel or rel['id'] not in samples:raise ValueError('unlinked sample')
        linked.append(samples[rel['id']])
    meta=lambda key:Counter(v['value'] for z in linked for v in z['attributes'].get('sample-metadata',[]) if v['key']==key and v.get('value'))
    material=meta('environment (material)');feature=meta('environment (feature)')
    if set(material)!={'UBERON:0002097'} or set(feature)!={'ENVO:2100003'}:raise ValueError('unexpected site metadata')
    return {'study':STUDY,'source':source,'api_pages':pages,'ontology':{'material':ontology('UBERON:0002097','uberon'),'feature':ontology('ENVO:2100003','envo')},
            'raw_ssu_columns':len(raw),'nonzero_ssu_columns':t.shape[1],'retained_columns':len(x),'retained_taxa':x.shape[1],
            'analysis_count':len(records['analyses']),'sample_count':len(samples),
            'exact_retained_run_matches':len(set(x.index)&byrun.keys()),'selected_pipeline_5_0_analyses':len(selected),
            'retained_run_analysis_version_multiplicity':dict(Counter(len(byrun[k]) for k in x.index)),
            'exact_retained_assembly_matches':len(set(x.index)&byassembly.keys()),
            'linked_sample_relationships':len(linked),'unique_linked_sample_ids':len({z['id'] for z in linked}),
            'linked_environment_material':dict(material),'linked_environment_feature':dict(feature),
            'linked_sample_description_counts':dict(Counter(str(z['attributes'].get('sample-desc') or 'missing') for z in linked)),
            'linked_explicit_host_names':dict(meta('host scientific name')),
            'linked_normalized_species':dict(Counter(z['attributes'].get('species') or 'missing' for z in linked)),
            'scope':'exact viewed SSU columns link to current sample records with structured skin material/feature codes despite mixed stool/oral study text and digestive archive label; specimen truth and subject independence not independently verified; old BH unchanged'}
if __name__=='__main__':
    d=run();(ROOT/'results/mixed_site_column_identity.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
