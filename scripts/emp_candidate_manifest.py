"""Outcome-blind EMP metadata manifest; no dataset eligibility claims."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def main():
    old=pd.read_csv(ROOT/'data/raw/mgnify/manifest.csv')
    emp=pd.read_csv(ROOT/'data/source_family_candidates/EMP/emp_mapping_subset_2k.tsv',sep='\t',low_memory=False)
    old_accessions=set(old.secondary_accession.dropna().astype(str))
    filtered=emp[~emp.ebi_accession.astype(str).isin(old_accessions)]
    with_subject=filtered[filtered.host_subject_id.notna()]
    rows=[]
    for sid,g in with_subject.groupby('study_id'):
        if len(g)<20:continue
        rows.append({'study_id':int(sid),'metadata_rows':len(g),'distinct_subject_ids':int(g.host_subject_id.nunique()),
                     'ebi_accessions':sorted(g.ebi_accession.dropna().astype(str).unique()),
                     'subject_id_missing_rows_excluded':int((filtered[filtered.study_id==sid].host_subject_id.isna()).sum()),
                     'status':'metadata_and_biom_id_candidate_not_independent_test'})
    rows.sort(key=lambda r:(-r['metadata_rows'],r['study_id']))
    result={'subset_rows':len(emp),'exact_mirror_rows_excluded':len(emp)-len(filtered),
            'missing_subject_rows_after_exact_exclusion':int(filtered.host_subject_id.isna().sum()),
            'study_candidates_min20_rows_after_subject_filter':len(rows),
            'candidate_metadata_rows':sum(r['metadata_rows'] for r in rows),
            'independently_verified_test_datasets':0,'studies':rows,
            'note':'Exact mirror exclusion and metadata only; near duplicate/assay/licensing/subject mapping not independently verified.'}
    (ROOT/'results/emp_candidate_manifest.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!='studies'},indent=2))
if __name__=='__main__':main()
