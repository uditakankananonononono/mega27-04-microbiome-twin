"""Public study-metadata screen of eight frozen title-unflagged archive IDs."""
import hashlib
import json
from pathlib import Path
import requests
from requests.exceptions import RequestException
ROOT=Path(__file__).resolve().parents[1]
IDS=('MGYS00000633','MGYS00002238','MGYS00005154','MGYS00005230',
     'MGYS00006006','MGYS00006755','MGYS00006794','MGYS00006795')
BASE='https://www.ebi.ac.uk/metagenomics/api/v1/studies/'

def run(fetch=requests.get):
    out=[]
    for sid in IDS:
        url=BASE+sid
        try:response=fetch(url,timeout=20)
        except RequestException as exc:
            out.append({'accession':sid,'url':url,'http_status':None,'assay_status':'unverifiable_network_error',
                        'error_type':type(exc).__name__})
            continue
        row={'accession':sid,'url':url,'http_status':response.status_code,
             'response_sha256':hashlib.sha256(response.content).hexdigest()}
        if response.status_code==200:
            attrs=response.json()['data']['attributes']
            if attrs.get('accession')!=sid:raise ValueError('source accession mismatch')
            for src,dst in [('study-name','study_name'),('secondary-accession','secondary_accession'),('bioproject','bioproject'),('data-origination','data_origination')]:
                row[dst]=attrs.get(src)
            abstract=str(attrs.get('study-abstract') or '')
            # Only source-authored study-description phrases; these are not per-run assay certificates.
            row['description_phrases']=[v for v in ('ultra-deep metagenomic sequencing',
                'whole genome sequencing','V4 16S rRNA amplicons','16S rDNA sequencing') if v.lower() in abstract.lower()]
            row['assay_status']='study_description_only_not_run_verified' if row['description_phrases'] else 'unknown'
            row['abstract_sha256']=hashlib.sha256(abstract.encode()).hexdigest()
        else:row['assay_status']='unverifiable_http_failure'
        out.append(row)
    return {'rows':out,'n_rows':len(out),'basis':'live MGnify study endpoint, eight frozen archive IDs; no sample/run method assertion',
            'limits':'Study description is not a per-run assay certificate. Manifest biome and source organism/sampling context can disagree; no new independent source win.'}
if __name__=='__main__':
    x=run();(ROOT/'results/gut_unflagged_source_screen.json').write_text(json.dumps(x,indent=2)+'\n')
    print(json.dumps(x,indent=2))
