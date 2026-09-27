"""Post-inspection source-material check, locked by dated amendment."""
from collections import Counter
import json
from pathlib import Path
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
    # Prior exact-run evidence pins the source table and fully paged analysis/sample responses.
    # Re-read current sample pages and fail if their bytes differ from those pinned hashes.
    samples,sp=paged('samples')
    if [(x['url'],x['items'],x['declared_total']) for x in sp] != [(x['url'],x['items'],x['declared_total']) for x in previous['api_pages']['samples']]:
        raise ValueError('sample pagination changed from pinned exact-column check')
    if previous['retained_columns']!=previous['unique_linked_sample_ids'] or previous['retained_columns']!=400:
        raise ValueError('prior exact run-column mapping not one-to-one')
    fields=summarize_material(samples,expected=previous['sample_count'])
    if fields['environment (material)']!={'ENVO:feces':529}:
        raise ValueError('material not uniform across source samples')
    ap=previous['api_pages']['analyses']
    return {'study':STUDY,'amendment':'results/PREREG_20260927_feces_material_amendment.md',
            'source':previous['source'],'api_pages':{'analyses':ap,'samples':sp},
            'all_source_samples':len(samples),'sample_page_1_byte_hash_changed':sp[0]['sha256']!=previous['api_pages']['samples'][0]['sha256'],
            'exact_mapped_retained_run_columns':400,
            'unique_retained_linked_samples':previous['unique_linked_sample_ids'],
            'all_source_sample_metadata':fields,
            'inference':'all 529 current source sample records share the feces material label; the previously exactly mapped 400 distinct samples were a subset; changed first-page serialization prevents strict byte-level carryover to the earlier mapping',
            'scope':'post-inspection metadata-only feces compatibility; no independent specimen verification, person/family lineage, historical assay, rights or untouched benchmark'}
if __name__=='__main__':
    result=run();(ROOT/'results/gut_material_identity.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
