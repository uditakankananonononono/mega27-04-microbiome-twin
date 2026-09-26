"""Conservative exact-accession overlap audit, not a near-duplicate detector."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def main():
    old=pd.read_csv(ROOT/'data/raw/mgnify/manifest.csv')
    emp=pd.read_csv(ROOT/'data/source_family_candidates/EMP/emp_studies.csv')
    exact=emp[emp.ebi_accession.astype(str).isin(set(old.secondary_accession.dropna().astype(str)))]
    rows=[]
    for r in exact.itertuples():
        match=old[old.secondary_accession.astype(str)==str(r.ebi_accession)]
        rows.append({'emp_study_id':int(r.study_id),'emp_release1':bool(r.release1_study),
                     'ebi_accession':str(r.ebi_accession), 'mgnify_study_ids':sorted(match.study.tolist())})
    result={'emp_studies':len(emp),'emp_release1_catalog':int((emp.release1_study==True).sum()),
            'old_mgnify_studies':len(old),'exact_accession_overlaps':len(rows),
            'overlaps':rows,'status':'exact_accession_exclusion_only',
            'note':'No cross-BioProject/sample/sequence near-duplicate search yet; absence from this list does not prove independence.'}
    out=ROOT/'results/emp_mgnify_exact_overlap.json';out.write_text(json.dumps(result,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!='overlaps'},indent=2))
if __name__=='__main__':main()
