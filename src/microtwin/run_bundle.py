"""Local integrity receipts. Hash matching is not authenticity or scientific validation."""
import hashlib,json
from pathlib import Path

ROLES=('train','query','contracts','prediction')

def receipt(files,report):
    if not set(ROLES)<=set(files) or set(files)-set(ROLES)-{'subject_map','query_subject_map'}:raise ValueError('train/query/contracts/prediction and optional subject_map required')
    if not isinstance(report,dict):raise ValueError('run report object required')
    records={}
    for role,path in files.items():
        p=Path(path)
        if not p.is_file() or p.is_symlink() or p.stat().st_size>50_000_000:raise ValueError('missing, symbolic or oversized bundle input')
        data=p.read_bytes();records[role]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
    for role,field in [('train','train_sha256'),('query','query_sha256'),('contracts','contract_sha256')]:
        if report.get(field)!=records[role]['sha256']:raise ValueError('run report/input hash mismatch')
    if report.get('subject_map_sha256') is not None:
        if 'subject_map' not in records or records['subject_map']['sha256']!=report['subject_map_sha256']:raise ValueError('subject map hash required/mismatched')
    elif 'subject_map' in records:raise ValueError('unexpected subject map')
    if report.get('query_subject_map_sha256') is not None:
        if 'query_subject_map' not in records or records['query_subject_map']['sha256']!=report['query_subject_map_sha256']:raise ValueError('query map hash required/mismatched')
    elif 'query_subject_map' in records:raise ValueError('unexpected query subject map')
    if report.get('status')!='research_baseline_prediction' or not isinstance(report.get('measurement_contract'),dict):raise ValueError('strict checked baseline report required')
    return {'schema':'microtwin.local-integrity.v1','files':records,'run_report':report,'clinical_use':False,'external_validation':False,'note':'Local receipt only. Hashes detect byte changes against this receipt; an attacker replacing both files and receipt can evade it. No signature, identity, rights, independence or calibration certificate. Does not embed input tables.'}

def verify(manifest,files):
    p=Path(manifest)
    if not p.is_file() or p.is_symlink() or p.stat().st_size>1_000_000:raise ValueError('missing or oversized receipt')
    obj=json.loads(p.read_text())
    if not isinstance(obj,dict) or obj.get('schema')!='microtwin.local-integrity.v1':raise ValueError('unsupported receipt schema')
    if set(obj)!={'schema','files','run_report','clinical_use','external_validation','note'}:
        raise ValueError('receipt envelope fields must match schema exactly')
    if obj['clinical_use'] is not False or obj['external_validation'] is not False:
        raise ValueError('receipt cannot assert clinical use or external validation')
    rebuilt=receipt(files,obj.get('run_report',{}))
    if obj['note']!=rebuilt['note']:raise ValueError('receipt scope note mismatch')
    if obj.get('files')!=rebuilt['files']:raise ValueError('artifact integrity mismatch')
    return {'status':'local_artifact_hashes_match','schema':obj['schema'],'clinical_use':False,'external_validation':False,'note':rebuilt['note']}
