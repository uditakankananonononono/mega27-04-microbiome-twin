"""Metadata lineage screening; shared subjects do not certify paired specimens."""
from collections import defaultdict
import json,re
from pathlib import Path
FIELDS={'source','subject','specimen','collection','material','modality','aliquot_group','technical','condition','lineage_verified'}
MODALITIES={'qPCR','SCFA','bile_acid','LCN2','histology','metabolomics','16S','metagenomics'}
LABEL=re.compile(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,79}')
def deny():raise ValueError('specimen lineage metadata rejected')

def screen_lineage(obj):
    if type(obj) is not dict or set(obj)!={'schema','records','minimum_paired_specimens'} or obj['schema']!='microtwin.specimen-lineage.metadata.v1':deny()
    minimum=obj['minimum_paired_specimens']
    if type(minimum) is not int or not 1<=minimum<=10000:deny()
    rows=obj['records']
    if type(rows) is not list or not 1<=len(rows)<=10000:deny()
    seen=set();subjects=defaultdict(set);specimens=defaultdict(list);coords=defaultdict(set)
    for r in rows:
        if type(r) is not dict or set(r)!=FIELDS:deny()
        for k in FIELDS-{'lineage_verified','modality','specimen','aliquot_group'}:
            if type(r[k]) is not str or not LABEL.fullmatch(r[k]):deny()
        for k in ['specimen','aliquot_group']:
            if r[k] is not None and (type(r[k]) is not str or not LABEL.fullmatch(r[k])):deny()
        if type(r['lineage_verified']) is not bool or type(r['modality']) is not str or r['modality'] not in MODALITIES:deny()
        if r['lineage_verified'] and (r['specimen'] is None or r['aliquot_group'] is None):deny()
        key=(r['source'],r['subject'],r['specimen'],r['collection'],r['material'],r['modality'],r['technical'])
        if key in seen:deny()
        seen.add(key);subjects[(r['source'],r['subject'])].add(r['modality'])
        coord=(r['source'],r['subject'],r['collection'],r['material'],r['modality'])
        coords[coord].add(r['specimen'])
        if r['specimen'] is not None:specimens[(r['source'],r['specimen'])].append(r)
    shared=sum(len(v)>=2 for v in subjects.values());unknown=sum(r['specimen'] is None or r['aliquot_group'] is None or not r['lineage_verified'] for r in rows)
    conflicts=0;aliquot_conflicts=0;paired=0;label_pairs=0;repeat=0
    for ss in specimens.values():
        if len({(r['subject'],r['collection'],r['material'],r['condition']) for r in ss})!=1:
            conflicts+=1;continue
        mods={r['modality'] for r in ss};repeat+=len(ss)-len(mods)
        if len(mods)<2:continue
        label_pairs+=1
        groups={r['aliquot_group'] for r in ss}
        if len(groups)!=1:aliquot_conflicts+=1;continue
        if None not in groups and all(r['lineage_verified'] for r in ss):paired+=1
    ambiguous=sum(len(ids)>1 for ids in coords.values())
    reasons=[]
    for count,reason in [(unknown,'LINEAGE_UNVERIFIED_OR_UNKNOWN'),(conflicts,'SPECIMEN_PROVENANCE_CONFLICT'),(aliquot_conflicts,'ALIQUOT_LINEAGE_CONFLICT'),(ambiguous,'AMBIGUOUS_SPECIMEN_JOIN')]:
        if count:reasons.append({'reason':reason,'count':count})
    if paired<minimum:reasons.append({'reason':'INSUFFICIENT_VERIFIED_LABEL_PAIRS','count':minimum-paired})
    return {'status':'BLOCKED' if reasons else 'METADATA_READY_FOR_MANUAL_LINEAGE_REVIEW','metadata_rows':len(rows),'shared_subject_labels':shared,'cross_modality_specimen_label_candidates':label_pairs,'submitted_verified_specimen_pairs':paired,'technical_repeat_rows_not_additional_specimens':repeat,'unresolved_reasons':reasons,'physical_aliquot_source_verified':False,'outcome_admitted':False,'multimodal_validated':False,'note':'Submitted verification is not authenticated physical lineage. Shared subject labels and technical rows are not paired specimens; no outcome, causal or clinical claim.'}

def load_lineage(path):
    def pairs(items):
        d={}
        for k,v in items:
            if k in d:deny()
            d[k]=v
        return d
    try:
        p=Path(path)
        if not p.is_file() or p.is_symlink() or p.stat().st_size>2_000_000:deny()
        with p.open('rb') as f:raw=f.read(2_000_001)
        if len(raw)>2_000_000:deny()
        return screen_lineage(json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:deny()))
    except (OSError,ValueError,TypeError,UnicodeError,RecursionError):deny()
