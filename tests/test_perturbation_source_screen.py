import hashlib

import pandas as pd

import scripts.perturbation_source_screen as mod


def test_aggregate_screen_with_synthetic_metadata(tmp_path,monkeypatch):
    base=tmp_path/'data/source_family_candidates/PERTURB';base.mkdir(parents=True)
    old=tmp_path/'data/raw/mgnify';old.mkdir(parents=True)
    pd.DataFrame({'secondary_accession':['ERP_OLD']}).to_csv(old/'manifest.csv',index=False)
    datasets={
        'Hagan_2019_metadata.csv':pd.DataFrame({'study_accession':['SRP168524']*3,'run_accession':['r1','r2','r3'],
                                                'sample_accession':['s1','s2','s3'],'isolate':['a','a','b'],
                                                'Day of study':[0,3,0],'treatment':['drug','drug','control']}),
        'Palleja_2018_metadata.csv':pd.DataFrame({'study_accession':['ERP022986']*2,'run_accession':['r1','r2'],
                                                  'sample_accession':['s1','s1']}),
        'Taur_2018_metadata.csv':pd.DataFrame({'study_accession':['SRP162022']*2,'run_accession':['r1','r2'],
                                               'sample_accession':['s1','s2'],'patientID':[1,2],
                                               'library_strategy':['AMPLICON','WGS']}),
    }
    checks={}
    for name,frame in datasets.items():
        path=base/name;frame.to_csv(path,index=False)
        checks[name]=hashlib.sha256(path.read_bytes()).hexdigest()
    monkeypatch.setattr(mod,'ROOT',tmp_path)
    monkeypatch.setattr(mod,'BASE',base)
    monkeypatch.setattr(mod,'EXPECTED',checks)
    result=mod.screen()
    rows={r['source_name']:r for r in result['records']}
    assert result['verified_independent_perturbation_datasets']==0
    assert rows['Hagan_2019_metadata.csv']['distinct_subject_labels']==2
    assert rows['Palleja_2018_metadata.csv']['unique_sample_accessions']==1
    assert rows['Taur_2018_metadata.csv']['library_strategy_rows']['WGS']==1
    assert not any(r['exact_secondary_accession_in_old_mgnify_audit'] for r in rows.values())
