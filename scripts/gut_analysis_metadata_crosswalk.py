"""Aggregate MGnify analysis types and sample-host metadata, with no per-sample output."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parents[1]
CACHE=Path('/tmp/micro-mgnify-pages');CACHE.mkdir(exist_ok=True)
IDS=tuple(sorted(r['accession'] for r in json.loads((ROOT/'results/gut_unflagged_source_screen.json').read_text())['rows']))
BASE='https://www.ebi.ac.uk/metagenomics/api/v1/studies/'

def pages(sid,kind,fetch):
    url=f'{BASE}{sid}/{kind}?page_size=1000';seen_urls=set();items=[];proof=[];ids=set()
    while url:
        if url in seen_urls:raise ValueError('pagination loop')
        seen_urls.add(url)
        cache=CACHE/(hashlib.sha256(url.encode()).hexdigest()+'.json')
        if cache.exists():
            content=cache.read_bytes();body=json.loads(content);status=200
        else:
            response=fetch(url,timeout=20);response.raise_for_status()
            content=response.content;body=response.json();status=response.status_code
            cache.write_bytes(content)
        batch=body['data']
        for r in batch:
            if r['id'] in ids:raise ValueError(f'duplicate {kind} item')
            ids.add(r['id'])
        items.extend(batch)
        expected=body['meta']['pagination']['count']
        proof.append({'url':url,'http_status':status,'items':len(batch),
                      'response_sha256':hashlib.sha256(content).hexdigest(),
                      'declared_total':expected})
        url=body.get('links',{}).get('next')
    if len(items)!=proof[0]['declared_total'] or any(p['declared_total']!=len(items) for p in proof):
        raise ValueError('incomplete pagination or count changed during read')
    return items,proof

def run(fetch=requests.get, ids=IDS):
    out=[]
    for sid in ids:
        analyses,ap=pages(sid,'analyses',fetch)
        samples,sp=pages(sid,'samples',fetch)
        types=Counter(str(r.get('attributes',{}).get('experiment-type') or 'missing') for r in analyses)
        species=Counter(str(r.get('attributes',{}).get('species') or 'missing') for r in samples)
        taxids=Counter(str(r.get('attributes',{}).get('host-tax-id') or 'missing') for r in samples)
        hostnames=Counter()
        conflict=0;missing_host_name=0
        for r in samples:
            attrs=r.get('attributes',{});hosts={str(t.get('value')).strip() for t in (attrs.get('sample-metadata') or [])
                   if str(t.get('key','')).strip().lower()=='host scientific name' and t.get('value') is not None}
            hosts={h for h in hosts if h and h.lower() not in {'missing','not provided','unknown','not available','na','none'}}
            if not hosts:missing_host_name+=1
            for h in hosts:hostnames[h]+=1
            if hosts and attrs.get('species')=='Homo sapiens' and all(h.lower() not in {'homo sapiens','human'} for h in hosts):
                conflict+=1
        out.append({'study':sid,'analysis_count':len(analyses),'sample_count':len(samples),
                    'experiment_type_analysis_counts':dict(sorted(types.items())),
                    'normalized_sample_species_counts':dict(sorted(species.items())),
                    'normalized_sample_host_tax_id_counts':dict(sorted(taxids.items())),
                    'sample_metadata_host_scientific_name_counts':dict(sorted(hostnames.items())),
                    'human_normalized_vs_nonhuman_host_name_conflict_samples':conflict,
                    'samples_without_usable_host_name':missing_host_name,
                    'analysis_pages':ap,'sample_pages':sp})
    return {'rows':out,'scope':'public MGnify aggregate metadata for eight viewed audit records, no per-sample IDs or outcomes',
            'limits':'MGnify analysis types not yet mapped to exact original audit table columns; species and host-name conflicts unresolved. No independent validation.'}
if __name__=='__main__':
    import sys
    ids=tuple(sys.argv[1:]) or IDS
    if any(sid not in IDS for sid in ids):raise ValueError('study outside frozen set')
    x=run(ids=ids);(ROOT/('results/gut_analysis_metadata_crosswalk_'+('_'.join(ids))+'.json')).write_text(json.dumps(x,indent=2)+'\n')
    for r in x['rows']:print(r['study'],r['analysis_count'],r['experiment_type_analysis_counts'],r['normalized_sample_species_counts'],r['sample_metadata_host_scientific_name_counts'],r['human_normalized_vs_nonhuman_host_name_conflict_samples'],flush=True)
