"""Strict metadata-only nested culture design preflight, never outcome admission.

Verification flags are submitted assertions, not source-authenticated evidence.
"""
from collections import defaultdict,Counter
import json
import math
import re
from pathlib import Path

FIELDS={'study','experiment','biological_unit','technical_unit','condition',
        'control','batch','medium','time','removed_token','identity_verified'}
LABEL=re.compile(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,79}')


def deny():raise ValueError('nested perturbation metadata rejected')


def screen_nested_design(obj):
    if type(obj) is not dict or set(obj)!={'schema','expected_technical_units','minimum_biological_pairs','records'}:deny()
    if obj['schema']!='microtwin.nested-perturbation.metadata.v1':deny()
    expected=obj['expected_technical_units'];minimum=obj['minimum_biological_pairs']
    if type(expected) is not int or not 1<=expected<=100:deny()
    if type(minimum) is not int or not 2<=minimum<=100:deny()
    rows=obj['records']
    if type(rows) is not list or not 1<=len(rows)<=10000:deny()
    units=defaultdict(set);verified=defaultdict(list);technical=set();arms=defaultdict(lambda:defaultdict(set));contexts=defaultdict(set)
    # Each unit's treatment is invariant across technical replicates/medium/time.
    for r in rows:
        if type(r) is not dict or set(r)!=FIELDS:deny()
        for k in FIELDS-{'time','identity_verified','condition','control','removed_token'}:
            if type(r[k]) is not str or not LABEL.fullmatch(r[k]):deny()
        if r['condition'] not in ('control','removal') or type(r['condition']) is not str:deny()
        if r['control']!='full' or type(r['control']) is not str:deny()
        if type(r['identity_verified']) is not bool:deny()
        if type(r['time']) not in (int,float) or not math.isfinite(r['time']):deny()
        token=r['removed_token']
        if r['condition']=='control':
            if token is not None:deny()
        elif type(token) is not str or not LABEL.fullmatch(token):deny()
        unit=(r['study'],r['experiment'],r['biological_unit'])
        treatment=(r['condition'],token)
        units[unit].add(treatment);verified[unit].append(r['identity_verified'])
        context=(r['study'],r['experiment'],r['batch'],r['medium'],r['time'])
        technical_key=(unit,r['medium'],r['time'],r['technical_unit'])
        if technical_key in technical:deny()
        technical.add(technical_key)
        arm=(treatment,unit)
        arms[context][arm].add(r['technical_unit'])
        contexts[(r['study'],r['experiment'],r['medium'],r['time'])].add(treatment)
    conflicts=sum(len(v)>1 for v in units.values())
    unverified=sum(not all(v) for v in verified.values())
    # No division of well-count by expected count to invent biological n.
    incomplete=sum(len(t)!=expected for a in arms.values() for t in a.values())
    pairs=Counter();unmatched=0;ambiguous=0
    for context,a in arms.items():
        controls=[(u,t) for ((c,token),u),t in a.items() if c=='control']
        drops=[(token,u,t) for ((c,token),u),t in a.items() if c=='removal']
        if len(controls)!=1:
            unmatched+=len(drops) if not controls else 0
            ambiguous+=len(drops) if len(controls)>1 else 0
            continue
        cu,ct=controls[0]
        for token,u,t in drops:
            if len(ct)==expected and len(t)==expected:
                # Same batch is syntax pairing only; verification gate remains separate.
                pairs[(context[0],context[1],context[3],context[4],token)]+=1
            else:unmatched+=1
    low=sum(n<minimum for n in pairs.values())
    bystudy=defaultdict(list)
    for (study,experiment,medium,time),treatments in contexts.items():bystudy[(study,medium,time)].append(treatments)
    imbalance=sum(any(v!=ss[0] for v in ss[1:]) for ss in bystudy.values())
    reasons=[]
    for n,label in [(conflicts,'CONFLICTING_BIOLOGICAL_TREATMENT'),(unverified,'BIOLOGICAL_IDENTITIES_UNVERIFIED'),(incomplete,'INCOMPLETE_TECHNICAL_REPLICATION'),(unmatched,'UNMATCHED_OR_INCOMPLETE_CONTROL_PAIRS'),(ambiguous,'AMBIGUOUS_CONTROL_MATCH'),(imbalance,'CONDITION_EXPERIMENT_IMBALANCE'),(low,'INSUFFICIENT_COMPLETE_BIOLOGICAL_PAIRS')]:
        if n:reasons.append({'reason':label,'count':n})
    if not pairs:reasons.append({'reason':'NO_COMPLETE_LABEL_PAIRS','count':1})
    return {'status':'BLOCKED' if reasons else 'METADATA_READY_FOR_MANUAL_DESIGN_REVIEW',
            'technical_record_count':len(rows),'declared_biological_unit_count':len(units),
            'complete_label_pair_count':sum(pairs.values()),
            'unmatched_or_incomplete_pairs':unmatched,'ambiguous_control_pairs':ambiguous,
            'expected_technical_units':expected,'minimum_biological_pairs':minimum,
            'pair_coverage_counts':sorted(pairs.values()),'unresolved_reasons':reasons,
            'biological_identity_source_verified':False,'outcome_admitted':False,
            'intervention_validated':False,'eligible_untouched_holdout':False,
            'note':'Counts are submitted design labels, not verified independent preparations or causal effects. Technical wells are not biological n. Metadata readiness still requires source evidence review; no outcome access or admission.'}


def load_nested_design(path):
    def pairs(items):
        out={}
        for k,v in items:
            if k in out:deny()
            out[k]=v
        return out
    try:
        p=Path(path)
        if not p.is_file() or p.is_symlink() or p.stat().st_size>2_000_000:deny()
        with p.open('rb') as f:raw=f.read(2_000_001)
        if len(raw)>2_000_000:deny()
        return screen_nested_design(json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:deny()))
    except (OSError,ValueError,TypeError,UnicodeError,RecursionError):deny()
