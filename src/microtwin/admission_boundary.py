"""Metadata-only OMM12 v1 boundary consistency check, not grant authentication.

Unknown protocols fail closed. Never reads source workbooks or raw quarantine.
A consistent submitted certificate cannot establish rights or scientific truth.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

STATUS={
 'protocol':'OMM12-CULTURE-QPCR-AUDIT-v1',
 'source_family':'EXPOSED_CONTROLLED_CULTURE_DEVELOPMENT',
 'stage_A':'PASS','rights':'NO_CONTRARY_TEXT_NOTE_FOUND',
 'stage_B':'QUARANTINE_VALIDATED',
 'C1':'STRUCTURAL_SUBSET_ADMITTED_QUANTITATIVE_NOT_ADMITTED',
 'structural_C1':'ADMITTED_DOCUMENTARY_REPRESENTATION_COUNTS_ONLY',
 'quantitative_C1':'NOT_ADMITTED_LOCKED','quantitative_admission':'NOT_ADMITTED',
 'zero_semantics':'UNRESOLVED','C2':'BLOCKED','C3':'NOT_PROPOSED','useful_win':'NOT_TESTED'}
FIELDS=set(STATUS)|{'source_sha256','selected_rows','allowed_cells','manifest',
                    'representation_counts','issues','parent_decision_at'}
COUNTS={'AMBIGUOUS_ZERO','NUMERIC_REPRESENTATION_VALID'}
KEY=re.compile(r'(OMM12|OMM11-(KB1|YL2|KB18|YL27|YL31|YL32|YL44|YL45|I46|I48|I49|YL58))_E[123]_(AF|APF)_W[123]')
ADDRESS=re.compile(r'([B-M])([2-9]|[1-9][0-9]|1[0-9]{2}|2[01][0-9]|22[0-9])')


def _deny():
    # Fixed non-echoing failure, including errors inside nested values.
    raise ValueError('admission boundary certificate rejected')


def check_boundary(d):
    if type(d) is not dict or set(d)!=FIELDS:_deny()
    if any(type(d[k]) is not str or d[k]!=v for k,v in STATUS.items()):_deny()
    if type(d['source_sha256']) is not str or not re.fullmatch(r'[0-9a-f]{64}',d['source_sha256']):_deny()
    if type(d['parent_decision_at']) is not str or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}',d['parent_decision_at']):_deny()
    if type(d['selected_rows']) is not int or d['selected_rows']!=222:_deny()
    if type(d['allowed_cells']) is not int or d['allowed_cells']!=2664:_deny()
    c=d['representation_counts']
    if type(c) is not dict or set(c)!=COUNTS or any(type(v) is not int or v<0 for v in c.values()):_deny()
    if sum(c.values())!=d['allowed_cells']:_deny()
    if type(d['issues']) is not list or d['issues']:_deny()
    m=d['manifest']
    if type(m) is not list or len(m)!=d['selected_rows']:_deny()
    seen_keys=set();seen_addresses=set();seen_rows=set()
    for row in m:
        if type(row) is not dict or set(row)!={'sample_key','addresses'}:_deny()
        k=row['sample_key'];addresses=row['addresses']
        if type(k) is not str or not KEY.fullmatch(k) or k in seen_keys:_deny()
        if type(addresses) is not list or len(addresses)!=12:_deny()
        parsed=[]
        for a in addresses:
            if type(a) is not str or not ADDRESS.fullmatch(a) or a in seen_addresses:_deny()
            parsed.append(ADDRESS.fullmatch(a).groups());seen_addresses.add(a)
        if [a[0] for a in parsed]!=list('BCDEFGHIJKLM'):_deny()
        numbers={a[1] for a in parsed}
        if len(numbers)!=1 or next(iter(numbers)) in seen_rows:_deny()
        seen_rows.update(numbers);seen_keys.add(k)
    return {'status':'boundary_consistent_not_authenticated',
            'structural_C1':STATUS['structural_C1'],'quantitative_C1':STATUS['quantitative_C1'],
            'C2':STATUS['C2'],'C3':STATUS['C3'],'useful_win':STATUS['useful_win'],
            'source_family':STATUS['source_family'],'zero_semantics':'UNRESOLVED',
            'selected_rows':222,'manifest_cells':2664,
            'representation_counts':dict(c),'quantitative_admitted':False,
            'eligible_untouched_holdout':False,'can_auto_claim_win':False,
            'note':'Counts describe representations only. Submitted status consistency does not authenticate permission, rights, calibration, biological pairing or source independence.'}


def load_boundary(path):
    def pairs(items):
        d={}
        for k,v in items:
            if k in d:_deny()
            d[k]=v
        return d
    try:
        p=Path(path)
        if not p.is_file() or p.stat().st_size>1_000_000:_deny()
        # Bound read as well as stat to handle concurrent growth.
        with p.open('rb') as f:raw=f.read(1_000_001)
        if len(raw)>1_000_000:_deny()
        d=json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _: _deny())
        return check_boundary(d)
    except (OSError,ValueError,TypeError,RecursionError,UnicodeError):
        _deny()
