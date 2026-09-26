"""Outcome-blind aggregate design screen of the NUH antibiotic cohort.

Do not commit its subject-level abundance table. This code reads only the six
metadata columns and the column headers; values stay unexamined here.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'data/source_family_candidates/RECOVERY/NUH_StoolSamples_MetaPhlAn2.txt'
EXPECTED='c978b8469113c81ec1e54a8a99e555609d52671bc039e0f62c6ce7f8dba75224'


def screen():
    if hashlib.sha256(SRC.read_bytes()).hexdigest()!=EXPECTED:raise ValueError('NUH file checksum mismatch')
    with SRC.open() as h:
        fields=h.readline().rstrip('\n').split('\t')
    meta=['LibraryID','PatientID','Type','Days','Group','TimePoint']
    if fields[:6]!=meta or len(fields)!=len(set(fields)):
        raise ValueError('NUH header unexpected or duplicate column')
    d=pd.read_csv(SRC,sep='\t',usecols=meta,dtype={'PatientID':str,'LibraryID':str},low_memory=False)
    if d[meta].isna().any().any() or d.LibraryID.duplicated().any():
        raise ValueError('missing metadata or duplicate sample')
    if (d.groupby('PatientID').Group.nunique()!=1).any():raise ValueError('patient group conflict')
    groups=d.groupby('PatientID').TimePoint.apply(lambda x:set(x))
    phases=('PRE','DURING','POST')
    out={'status':'metadata_design_only_not_result','source_commit':'d374f5e7c09da659d407af5664604b81451c5df4',
         'source_sha256':EXPECTED,'profile_rows':len(d),'unique_library_ids':int(d.LibraryID.nunique()),
         'patient_labels':int(d.PatientID.nunique()),'group_patient_labels':{str(k):int(v) for k,v in d.groupby('Group').PatientID.nunique().items()},
         'timepoint_rows':{str(k):int(v) for k,v in d.TimePoint.value_counts().items()},
         'patient_labels_with_all_three_phases':int(sum(set(phases)<=v for v in groups)),
         'duplicate_patient_timepoints':int(d.duplicated(['PatientID','TimePoint']).sum()),
         'profile_columns':len(fields)-6,'taxonomic_hierarchy_columns':int(sum('|' in s for s in fields[6:])),
         'source_accessions':['PRJEB41865','PRJEB41866'],
         'note':'NUH source table metadata only. Group/patient labels are not a rights or independent-source check; taxonomic ancestors cannot be summed. No abundance outcomes or model errors examined; cohort is viewed for method development, not final untouched test.'}
    return out


def main():
    result=screen()
    (ROOT/'results/recovery_nuh_design.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
