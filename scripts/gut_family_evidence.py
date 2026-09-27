"""Aggregate source-family and participant-label diagnostic without sample rows."""
from collections import Counter
from hashlib import sha256
import json
from scripts.gut_candidate_column_identity import ROOT, STUDY, paged, get

def run():
    study_url=f'https://www.ebi.ac.uk/metagenomics/api/v1/studies/{STUDY}'
    study_bytes,study_ref=get(study_url)
    study=json.loads(study_bytes)['data']['attributes']
    publication_url=f'https://www.ebi.ac.uk/metagenomics/api/v1/studies/{STUDY}/publications'
    publication_bytes,publication_ref=get(publication_url)
    publications=json.loads(publication_bytes).get('data',[])
    samples,pages=paged('samples')
    keys=Counter(k.strip().lower() for s in samples for v in s['attributes'].get('sample-metadata',[])
                 if (k:=str(v.get('key') or '')))
    flagged={k:v for k,v in keys.items() if any(word in k for word in
                 ('subject','participant','person','individual','family','household','donor','patient','host id','host_id'))}
    return {'study':STUDY,'study_source':study_ref,'sample_sources':pages,'linked_publication_source':publication_ref,
            'linked_publications':[{'pubmed_id':p['attributes'].get('pubmed-id'),
             'doi':p['attributes'].get('doi'),'title':p['attributes'].get('pub-title')} for p in publications],
            'bioproject':study.get('bioproject'),'secondary_accession':study.get('secondary-accession'),
            'declared_samples':study.get('samples-count'),'retrieved_samples':len(samples),
            'metadata_key_counts':dict(keys),'possible_participant_or_family_key_counts':flagged,
            'source_family_independence_status':'unknown',
            'scope':'aggregate current provider metadata for viewed source only; study abstract corresponds to a 2012 paper but linked-publication endpoint lists a different 2021 paper, so publication association is not certified; absence of key names does not prove no participant IDs exist in primary data; no mirror, rights, historical assay or subject-independence certificate'}
if __name__=='__main__':
    d=run();(ROOT/'results/gut_family_evidence.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
