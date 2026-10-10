"""Unsigned local receipts for four fixed public evidence artifacts, no outcomes."""
import hashlib
import json
from pathlib import Path
from .admission_boundary import load_boundary

ROOT=Path(__file__).resolve().parents[2]
FILES={
 'proposal':'OMM12_OUTCOME_ADMISSION_PROPOSAL_20261010.md',
 'closeout':'OMM12_DOCUMENTARY_CLOSEOUT_20261010.md',
 'certificate':'omm12_quarantine_certificate_20261010.json',
 'boundary_check':'omm12_platform_boundary_check_20261010.json'}
SCHEMA='microtwin.admission-evidence.local-integrity.v1'
NOTE='Unsigned local integrity only, not authenticity or scientific validity. Replacing both receipt and accepted files can evade hash comparison. No source workbook, ZIP, private quarantine, numerical admission or biological certification.'


def deny():raise ValueError('admission evidence bundle rejected')


def read_safe(p):
    p=Path(p)
    if any(x.is_symlink() for x in [p,*p.parents]):deny()
    if not p.is_file() or p.stat().st_size>1_000_000:deny()
    with p.open('rb') as f:data=f.read(1_000_001)
    if len(data)>1_000_000:deny()
    return data


def parse(data):
    def pairs(items):
        d={}
        for k,v in items:
            if k in d:deny()
            d[k]=v
        return d
    return json.loads(data,object_pairs_hook=pairs,parse_constant=lambda _:deny())


def build_receipt(evidence_dir=None):
    try:
        base=Path(evidence_dir) if evidence_dir is not None else ROOT/'results'
        if not base.is_dir() or any(x.is_symlink() for x in [base,*base.parents]):deny()
        paths={r:base/n for r,n in FILES.items()}
        data={r:read_safe(p) for r,p in paths.items()}
        # Restrict document roles to recognized documentary structure, never raw JSON.
        for r,title in [('proposal','# OMM12 outcome-admission proposal v1,'),('closeout','# OMM12 documentary closeout,')]:
            text=data[r].decode('utf-8')
            if not text.startswith(title) or '\x00' in text:deny()
        report=load_boundary(paths['certificate'])
        if parse(data['boundary_check'])!=report:deny()
        return {'schema':SCHEMA,'roles':{r:{'filename':FILES[r],'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)} for r,b in data.items()},'boundary':report,'quantitative_admission':False,'source_outcome_access':False,'note':NOTE}
    except (OSError,ValueError,TypeError,UnicodeError,RecursionError):deny()


def create_receipt(out,*,evidence_dir=None):
    try:
        obj=build_receipt(evidence_dir);p=Path(out)
        if p.suffix!='.json' or p.exists() or p.is_symlink() or any(x.is_symlink() for x in p.parents):deny()
        # No document overwrite and no caller-selected input paths.
        with p.open('x') as f:json.dump(obj,f,indent=2);f.write('\n')
        return {'status':'local_evidence_receipt_created','quantitative_admission':False,'source_outcome_access':False,'note':NOTE}
    except (OSError,ValueError,TypeError,UnicodeError,RecursionError):deny()


def verify_receipt(path,*,evidence_dir=None):
    try:
        obj=parse(read_safe(path))
        if obj!=build_receipt(evidence_dir):deny()
        return {'status':'local_evidence_hashes_and_boundary_match','quantitative_admission':False,'source_outcome_access':False,'note':NOTE}
    except (OSError,ValueError,TypeError,UnicodeError,RecursionError):deny()
