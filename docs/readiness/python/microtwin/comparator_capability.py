"""Pre-outcome fairness declarations, not scores or authenticated benchmark proof."""
import json,re
from pathlib import Path
LABEL=re.compile(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,79}')
TASKS={'composition_forecast','removal_response','direction_forecast'}
OUTPUTS={'relative_composition','normalized_qPCR_disturbance','direction'}
INFO={'preintervention_composition','strain_traits','preintervention_history'}
MODEL_FIELDS={'role','task','output','horizon','input_information','capability','adapter','tuning_trials','failure_policy'}
FIELDS={'schema','task','output','horizon','allowed_information','protocol_timing','comparator_selection','test_source_status','models'}
def deny():raise ValueError('comparator capability metadata rejected')

def screen_comparators(d):
    if type(d) is not dict or set(d)!=FIELDS or d['schema']!='microtwin.comparator-capability.metadata.v1':deny()
    if type(d['task']) is not str or d['task'] not in TASKS or type(d['output']) is not str or d['output'] not in OUTPUTS:deny()
    if type(d['horizon']) is not str or not LABEL.fullmatch(d['horizon']):deny()
    expected_output={'composition_forecast':'relative_composition','removal_response':'normalized_qPCR_disturbance','direction_forecast':'direction'}
    if d['output']!=expected_output[d['task']]:deny()
    for k,vocab in [('protocol_timing',{'frozen_before_outcomes','unknown','retrospective'}),('comparator_selection',{'frozen_before_test','unknown','retrospective'}),('test_source_status',{'untouched_independence_reviewed','exposed','unknown'})]:
        if type(d[k]) is not str or d[k] not in vocab:deny()
    def info(x):
        if type(x) is not list or not x or any(type(v) is not str or v not in INFO for v in x) or len(set(x))!=len(x):deny()
        return set(x)
    allowed=info(d['allowed_information']);models=d['models']
    if type(models) is not list or not 2<=len(models)<=100:deny()
    reasons=[];candidates=0;budgets=[];actual_infos=[]
    for m in models:
        if type(m) is not dict or set(m)!=MODEL_FIELDS:deny()
        if type(m['role']) is not str or m['role'] not in ('candidate','comparator'):deny()
        candidates+=m['role']=='candidate'
        if type(m['task']) is not str or m['task'] not in TASKS or type(m['output']) is not str or m['output'] not in OUTPUTS:deny()
        if type(m['horizon']) is not str or not LABEL.fullmatch(m['horizon']):deny()
        if type(m['tuning_trials']) is not int or not 0<=m['tuning_trials']<=100000:deny()
        for k,vocab in [('capability',{'implemented','unsupported','unknown'}),('adapter',{'verified','missing','not_needed','unknown'}),('failure_policy',{'retain_all','drop_failures','unknown'})]:
            if type(m[k]) is not str or m[k] not in vocab:deny()
        mi=info(m['input_information']);actual_infos.append(mi);budgets.append(m['tuning_trials'])
        if mi-allowed:reasons.append('UNAUTHORIZED_EXTRA_INPUT_INFORMATION')
        if (m['task'],m['output'],m['horizon'])!=(d['task'],d['output'],d['horizon']):reasons.append('NOT_SAME_TASK_OUTPUT_HORIZON')
        if m['capability']!='implemented':reasons.append('COMPARATOR_OR_CANDIDATE_CAPABILITY_UNSUPPORTED_OR_UNKNOWN')
        if m['adapter'] not in ('verified','not_needed'):reasons.append('ADAPTER_MISSING_OR_UNKNOWN')
        if m['failure_policy']!='retain_all':reasons.append('FAILED_RUNS_NOT_PRESERVED')
    if candidates!=1:deny()
    if any(x!=actual_infos[0] for x in actual_infos[1:]):reasons.append('UNEQUAL_INFORMATION_SET')
    if len(set(budgets))!=1:reasons.append('UNEQUAL_DECLARED_TUNING_BUDGET')
    if d['protocol_timing']!='frozen_before_outcomes':reasons.append('PROTOCOL_NOT_PROSPECTIVELY_FROZEN')
    if d['comparator_selection']!='frozen_before_test':reasons.append('COMPARATOR_SELECTION_NOT_FROZEN_BEFORE_TEST')
    if d['test_source_status']!='untouched_independence_reviewed':reasons.append('TEST_SOURCE_EXPOSED_OR_UNKNOWN')
    return {'status':'BLOCKED' if reasons else 'DECLARED_FAIR_PLAN_READY_FOR_MANUAL_REVIEW','model_count':len(models),'blockers':sorted(set(reasons)),'fairness_source_verified':False,'losses_consumed':False,'external_benchmark_eligible':False,'win_certified':False,'note':'Equal declared budgets/information and submitted capability flags require source review. Unsupported tasks cannot be scored as model failures. No losses, fit, holdout certification or win.'}

def load_comparators(path):
    def pairs(items):
        out={}
        for k,v in items:
            if k in out:deny()
            out[k]=v
        return out
    try:
        p=Path(path)
        if not p.is_file() or p.is_symlink() or p.stat().st_size>100000:deny()
        with p.open('rb') as f:raw=f.read(100001)
        if len(raw)>100000:deny()
        return screen_comparators(json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:deny()))
    except (OSError,ValueError,TypeError,UnicodeError,RecursionError):deny()
