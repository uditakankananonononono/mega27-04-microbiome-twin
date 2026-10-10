"""Semantic declarations only, no numbers, conversions or admission."""
import json
from pathlib import Path
VOCAB={
 'unit':{'normalized_16S_copies_per_ml','relative_abundance','concentration','counts','unknown'},
 'normalization':{'verified_applied','not_applicable_verified','definition_only','unknown'},
 'zero_interpretation':{'true_zero','below_DTL','excluded','missing','unknown'},
 'missing_convention':{'explicit_separate_flags','omitted_with_map','zero_encoded','unknown'},
 'DTL_policy':{'excluded','censored_flagged','not_applicable_verified','unknown'},
 'provenance_status':{'evidence_reviewed','definition_only','unknown'}}
FIELDS={'schema',*VOCAB}
def deny():raise ValueError('censoring contract rejected')

def assess_censor_contract(d):
    if type(d) is not dict or set(d)!=FIELDS or d['schema']!='microtwin.censor-semantics.metadata.v1':deny()
    for k,v in VOCAB.items():
        if type(d[k]) is not str or d[k] not in v:deny()
    reasons=[]
    for k in VOCAB:
        if d[k]=='unknown' or (k in ('normalization','provenance_status') and d[k]=='definition_only'):
            reasons.append('UNRESOLVED_'+k.upper())
    if d['zero_interpretation'] in ('below_DTL','excluded','missing'):
        reasons.append('ZERO_IS_NOT_QUANTITATIVE_ABSENCE')
    if d['missing_convention']=='zero_encoded':reasons.append('MISSING_ZERO_ENCODING_UNSAFE')
    if d['zero_interpretation']=='below_DTL' and d['DTL_policy']=='not_applicable_verified':reasons.append('CONTRADICTORY_DTL_SEMANTICS')
    if d['zero_interpretation']=='excluded' and d['DTL_policy']=='censored_flagged':reasons.append('CONTRADICTORY_EXCLUSION_SEMANTICS')
    if d['unit']=='normalized_16S_copies_per_ml' and d['normalization']=='not_applicable_verified':reasons.append('CONTRADICTORY_NORMALIZATION_SEMANTICS')
    return {'status':'ABSTAIN' if reasons else 'SEMANTIC_DECLARATIONS_READY_FOR_MANUAL_REVIEW',
            'unresolved_or_blocking_reasons':reasons,
            'quantitative_summary_eligible':False,'effect_eligible':False,'C1_admitted':False,
            'values_consumed':False,'conversion_or_imputation_performed':False,
            'note':'Submitted semantic labels cannot authenticate evidence, calibration or rights. Ready declarations require source review; zero, censoring, exclusion and missingness are never converted into each other.'}

def load_censor_contract(path):
    def pairs(items):
        d={}
        for k,v in items:
            if k in d:deny()
            d[k]=v
        return d
    try:
        p=Path(path)
        if not p.is_file() or p.is_symlink() or p.stat().st_size>10000:deny()
        with p.open('rb') as f:raw=f.read(10001)
        if len(raw)>10000:deny()
        return assess_censor_contract(json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:deny()))
    except (OSError,ValueError,TypeError,UnicodeError,RecursionError):deny()
