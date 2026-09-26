"""Outcome-blind aggregate screen of Harris rotavirus-antibiotic metadata.

Participant-level source map is fetched privately, hashed, summarized and
removed. Do not commit it: it contains clinical and symptom fields.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data/source_family_candidates/HARRIS/mapping_human_volunteer.txt'
EXPECTED='9d3ff3a057dfec48de2b9b2dd30620929d6573d3e41f436cb66d874ded056c5c'


def main():
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=EXPECTED:
        raise ValueError('Harris mapping source SHA256 mismatch')
    d=pd.read_csv(SOURCE,sep='\t',dtype=str,low_memory=False)
    needed=['#SampleID','patient_ID','day','randomization_arm','sample_surviving_dada2']
    if not set(needed)<=set(d.columns):raise ValueError('missing required study-design columns')
    if d['#SampleID'].duplicated().any():raise ValueError('duplicate sample ID')
    if d['#SampleID'].isna().any() or d.patient_ID.isna().any():raise ValueError('missing sample or subject ID')
    tab=d[needed].copy()
    out={'status':'metadata_design_only_no_outcomes',
         'source_commit':'3f7f111550e6cdccefb258d1275aff149f6ba9f0',
         'source_sha256':EXPECTED,'metadata_rows':len(tab),
         'distinct_sample_ids':int(tab['#SampleID'].nunique()),
         'distinct_patient_labels':int(tab.patient_ID.nunique()),
         'day_rows':{str(k):int(v) for k,v in tab.day.value_counts(dropna=False).items()},
         'arm_subjects':{str(k):int(v) for k,v in tab.groupby('randomization_arm').patient_ID.nunique().items()},
         'retained_dada2_rows':int(tab.sample_surviving_dada2.notna().sum()),
         'missing_subject_rows':int(tab.patient_ID.isna().sum()),
         'subject_arm_conflicts':int((tab.groupby('patient_ID').randomization_arm.nunique()>1).sum()),
         'subject_day_duplicates':int(tab.duplicated(['patient_ID','day']).sum()),
         'matched_subjects_day_0_7':int(sum({'0','7'}<=set(group.day.dropna()) for _,group in tab.groupby('patient_ID'))),
         'note':'Metadata counts only. Source map includes clinical fields and is not committed. No taxon table, baseline-only model, intervention direction, independence, source rights or benchmark result verified.'}
    (ROOT/'results/harris_metadata_screen.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()
