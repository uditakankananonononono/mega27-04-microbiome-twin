"""Outcome-blind DIABIMMUNE 16S/event metadata screen.

Only matrix header IDs and event-subject/time fields are read. The full OTU
matrix and clinical supplement are local, re-fetchable, and not committed.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/source_family_candidates/DIABIMMUNE'
MATRIX=BASE/'otu_table.filtered.2Maaslin.txt'
SUPPLEMENT=BASE/'aad0917.SuppTable1.xlsx'
EXPECTED_MATRIX='f202686dd96f1c6c1ec9f2b6e8c70ff0f7da655cc2697e6d91998442bf7b35bc'
EXPECTED_XLSX='b62f7f84633d1f07789731c14985c58fca80b81f8bb6348b49a79f15b0213da8'


def screen():
    import openpyxl
    if hashlib.sha256(MATRIX.read_bytes()).hexdigest()!=EXPECTED_MATRIX:raise ValueError('OTU table checksum mismatch')
    if hashlib.sha256(SUPPLEMENT.read_bytes()).hexdigest()!=EXPECTED_XLSX:raise ValueError('converted supplement checksum mismatch')
    with MATRIX.open() as f:header=next(csv.reader(f,delimiter='\t'))
    if header[0]!='sample' or len(header)!=len(set(header)):raise ValueError('invalid matrix header')
    ages=defaultdict(list)
    for s in header[1:]:
        try:p,a=s.split('_',1);ages[p].append(float(a))
        except (ValueError,TypeError):raise ValueError('unparseable sample age')
    w=openpyxl.load_workbook(SUPPLEMENT,read_only=True,data_only=True)
    general=[r[0] for r in list(w['General'].values)[1:] if r[0]]
    if len(general)!=len(set(general)):raise ValueError('duplicate general subject')
    events=[r for r in list(w['Antibiotics'].values)[1:] if r[0] and isinstance(r[1],(int,float))]
    match_subjects=set(ages)&set(general)
    affected=set(r[0] for r in events)&set(ages)
    event_prepost=0;people_prepost=set()
    for row in events:
        p,t=row[0],float(row[1])
        if p in ages and any(a<t for a in ages[p]) and any(a>t for a in ages[p]):
            event_prepost+=1;people_prepost.add(p)
    return {'status':'metadata_header_screen_only_no_model_outcomes',
            'matrix_sha256':EXPECTED_MATRIX,'converted_supplement_sha256':EXPECTED_XLSX,
            'matrix_columns':len(header)-1,'matrix_subject_prefixes':len(ages),
            'supplement_general_subjects':len(general),'general_matrix_overlap_subjects':len(match_subjects),
            'matrix_only_subject_prefixes':len(set(ages)-set(general)),
            'general_only_subjects':len(set(general)-set(ages)),
            'antibiotic_event_rows':len(events),'antibiotic_event_subjects':len(set(r[0] for r in events)),
            'antibiotic_event_subjects_with_matrix':len(affected),
            'event_rows_with_any_prepost_matrix_samples':event_prepost,
            'subjects_with_any_prepost_event':len(people_prepost),
            'note':'Repeated antibiotic courses are not independent experimental units. Infant development confounds time changes. Source sample metadata and converted sheet require identity/rights verification. Matrix abundance values not read; viewed for design development, not untouched final test.'}


def main():
    out=screen();(ROOT/'results/diabimmune_design.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
