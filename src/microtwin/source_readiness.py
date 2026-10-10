"""One bounded public metadata packet; no auto-admission or source authentication."""
import json
from pathlib import Path
from .admission_boundary import load_boundary
from .admission_evidence_bundle import verify_receipt
from .nested_perturbation_design import load_nested_design
from .specimen_lineage import load_lineage
from .censor_contract import load_censor_contract
from .comparator_capability import load_comparators
ROLES={'boundary','design','lineage','semantics','fairness','evidence_receipt'}
LOADERS={'boundary':load_boundary,'design':load_nested_design,'lineage':load_lineage,'semantics':load_censor_contract,'fairness':load_comparators}
EXPECTED={'boundary':'boundary_consistent_not_authenticated','design':'METADATA_READY_FOR_MANUAL_DESIGN_REVIEW','lineage':'METADATA_READY_FOR_MANUAL_LINEAGE_REVIEW','semantics':'SEMANTIC_DECLARATIONS_READY_FOR_MANUAL_REVIEW','fairness':'DECLARED_FAIR_PLAN_READY_FOR_MANUAL_REVIEW','evidence_receipt':'local_evidence_hashes_and_boundary_match'}

def deny():raise ValueError('source readiness metadata packet rejected')

def packet(directory):
    def pairs(items):
        d={}
        for k,v in items:
            if k in d:deny()
            d[k]=v
        return d
    try:
        base=Path(directory)
        if not base.is_dir() or any(p.is_symlink() for p in [base,*base.parents]):deny()
        config=base/'readiness_inputs.json'
        if config.is_symlink() or config.stat().st_size>10000:deny()
        with config.open('rb') as f:raw=f.read(10001)
        if len(raw)>10000:deny()
        obj=json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:deny())
        if type(obj) is not dict or set(obj)!={'schema','roles'} or obj['schema']!='microtwin.source-readiness.metadata.v1':deny()
        roles=obj['roles']
        if type(roles) is not dict or set(roles)!=ROLES:deny()
        for n in roles.values():
            if type(n) is not str or not n or Path(n).name!=n or not n.endswith('.json') or n in ('.','..'):deny()
            p=base/n
            if p.is_symlink() or not p.is_file():deny()
        if len(set(roles.values()))!=len(roles):deny()
        results={r:load(base/roles[r]) for r,load in LOADERS.items()}
        results['evidence_receipt']=verify_receipt(base/roles['evidence_receipt'],evidence_dir=base)
        domains={}
        for r,d in results.items():
            reasons=d.get('blockers',d.get('unresolved_reasons',d.get('unresolved_or_blocking_reasons',[])))
            domains[r]={'status':d['status'],'blocking':d['status']!=EXPECTED[r],'reasons':reasons}
        blocked=any(d['blocking'] for d in domains.values())
        return {'status':'BLOCKED' if blocked else 'DECLARATIONS_READY_FOR_MANUAL_REVIEW',
                'domains':domains,'quantitative_C1':'NOT_ADMITTED_LOCKED','C2':'BLOCKED','C3':'NOT_PROPOSED','useful_win':'NOT_TESTED',
                'outcomes_consumed':False,'scientific_goals_completed':False,'auto_admission':False,
                'note':'Public metadata consistency only. No authenticated source truth, scientific admission, discovery, benchmark win or clinical deployment. Manual review remains required even if every submitted domain is consistent.'}
    except (OSError,ValueError,TypeError,UnicodeError,RecursionError):deny()
