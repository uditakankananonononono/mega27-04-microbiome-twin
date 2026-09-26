"""Outcome-blind source identity screen of public antibiotic cohorts.

Metadata is fetched by exact pinned URLs and hashes. This is not a scored
forecast, perturbation-direction evaluation, or clinical finding.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/source_family_candidates/PERTURB'
EXPECTED={
    'Hagan_2019_metadata.csv':'d52985b791da5824b17905eb4bf0196ff948a0fed4c9e833d6bb8f0fde9f7757',
    'Palleja_2018_metadata.csv':'774ba99a5daa6a8a0a4ec5849f082e9a836efea5f9db80e539b5d35494e718b6',
    'Taur_2018_metadata.csv':'459aeba1de3ced0c2cfaedc9dc9abc61e9bacdda2c15a83586b037816dc8dfdf',
}
ACCESSIONS={'Hagan_2019_metadata.csv':'SRP168524','Palleja_2018_metadata.csv':'ERP022986',
            'Taur_2018_metadata.csv':'SRP162022'}


def screen():
    old=pd.read_csv(ROOT/'data/raw/mgnify/manifest.csv')
    archive=set(old.secondary_accession.dropna().astype(str))
    records=[]
    for name,sha in EXPECTED.items():
        file=BASE/name
        if hashlib.sha256(file.read_bytes()).hexdigest()!=sha:raise ValueError(f'{name}: checksum mismatch')
        d=pd.read_csv(file,low_memory=False)
        accession=ACCESSIONS[name]
        if d.study_accession.dropna().astype(str).unique().tolist()!=[accession]:
            raise ValueError(f'{name}: accession mismatch')
        r={'source_name':name,'secondary_accession':accession,'metadata_rows':len(d),
           'unique_runs':int(d.run_accession.nunique()),'unique_sample_accessions':int(d.sample_accession.nunique()),
           'exact_secondary_accession_in_old_mgnify_audit':accession in archive,
           'source_sha256':sha,'status':'candidate_metadata_not_eligible_perturbation_validation'}
        if name.startswith('Hagan'):
            if d.isolate.isna().any() or d['Day of study'].isna().any() or d.treatment.isna().any():
                raise ValueError('Hagan missing primary labels')
            if (d.groupby('isolate').treatment.nunique()!=1).any():raise ValueError('inconsistent Hagan subject treatment')
            r.update({'distinct_subject_labels':int(d.isolate.nunique()),
                      'distinct_timepoint_labels':int(d['Day of study'].nunique()),
                      'subject_day_duplicates':int(d.duplicated(['isolate','Day of study']).sum()),
                      'treatment_subject_counts':{k:int(v) for k,v in d.groupby('treatment').isolate.nunique().items()},
                      'note':'Original paper reports phase 1: 22 participants (11 antibiotics); phase 2: 11 (5 antibiotics). Combined 33 labels match the deposited metadata; phase identity per sample is not independently verified.'})
        elif name.startswith('Palleja'):
            r.update({'runs_per_unique_sample':round(len(d)/d.sample_accession.nunique(),3),
                      'subject_and_treatment_labels_in_this_metadata':False,
                      'note':'The curated accession table alone has no per-person or intervention day key; 114 runs are only 57 unique sample accessions.'})
        elif name.startswith('Taur'):
            r.update({'nonmissing_patientID_rows':int(d.patientID.notna().sum()),
                      'distinct_patientID_labels':int(d.patientID.nunique()),
                      'library_strategy_rows':{str(k):int(v) for k,v in d.library_strategy.value_counts(dropna=False).items()},
                      'note':'Most records have patient/day labels, but 14 WGS runs mixed with 16S, and transplant/FMT/antibiotic treatment labels require original-protocol reconciliation.'})
        records.append(r)
    out={'status':'source_metadata_screen_only','source_commit':'39372a71a2814462b728561bdf38598299e345ac',
         'records':records,'verified_independent_perturbation_datasets':0,
         'note':'Metadata availability and exact old-accession absence do not prove source independence, consent, cross-assay compatibility, or valid intervention predictions. No taxon outcomes read or scored.'}
    return out


def main():
    out=screen()
    (ROOT/'results/perturbation_source_screen.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
