"""Outcome-blind design screen of ARMORD source-data archive metadata."""
import csv
import hashlib
import io
import json
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

SOURCE_SHA='b57b1afcca8db8d101872d627cbdfd0d316bb64f321487c9d9318499c58d6c3b'
CODE_SHA='7b965b3b614d01eaa08e301c9411229ffc7556ed5803271c6ba93b409833ce38'
PREFIX='Source Data 1/study data/'
CODE_PREFIX='Source Code 1/ARMORD R project/armord_data/model_data/'

def screen(path, expected_sha=SOURCE_SHA, *, code_archive=None, expected_code_sha=CODE_SHA):
    if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=expected_sha:
        raise ValueError('source checksum mismatch')
    with zipfile.ZipFile(path) as z:
        def read(name):
            with z.open(PREFIX+name) as f:
                return list(csv.DictReader(io.TextIOWrapper(f,encoding='utf-8-sig')))
        samples=read('Samples.csv');patients=read('Patients.csv');exposures=read('Antimicrobial_exposures.csv')
    if not samples or not patients or not exposures:raise ValueError('missing metadata rows')
    if len({r['samp_id'] for r in samples})!=len(samples):raise ValueError('duplicate sample')
    people={r['pid']:r['category'] for r in patients}
    if len(people)!=len(patients) or not {r['pid'] for r in samples}<=people.keys():raise ValueError('patient map mismatch')
    times=defaultdict(list)
    for r in samples:times[r['pid']].append(float(r['collected_days_after_first_sample']))
    prepost=[];invalid=0;reversed_intervals=0
    for r in exposures:
        try:a=float(r['firstdose_days_after_first_sample']);b=float(r['lastdose_days_after_first_sample'])
        except ValueError:invalid+=1;continue
        if b<a:reversed_intervals+=1;continue
        if any(t<a for t in times[r['pid']]) and any(t>b for t in times[r['pid']]):prepost.append((r['pid'],a,b))
    pair_qc={}
    if code_archive is not None:
        if hashlib.sha256(Path(code_archive).read_bytes()).hexdigest()!=expected_code_sha:
            raise ValueError('published code archive checksum mismatch')
        with zipfile.ZipFile(code_archive) as z:
            with z.open(CODE_PREFIX+'l_patients.csv') as f:
                model_people=list(csv.DictReader(io.TextIOWrapper(f,encoding='utf-8-sig')))
            with z.open(CODE_PREFIX+'l_pairs.csv') as f:
                model_pairs=list(csv.DictReader(io.TextIOWrapper(f,encoding='utf-8-sig')))
        if len({r['pid'] for r in model_people})!=len(model_people):raise ValueError('duplicate model patient')
        pair_qc={'published_code_archive_sha256':expected_code_sha,
                 'model_input_longitudinal_patient_rows':len(model_people),
                 'model_input_pair_rows':len(model_pairs),
                 'model_input_pair_contributing_people':len({r['pid'] for r in model_pairs}),
                 'model_pair_people_not_in_patient_map':len({r['pid'] for r in model_pairs}-{r['pid'] for r in model_people})}
    return {'status':'metadata_only_no_taxon_outcomes','source_archive_sha256':expected_sha,
            'sequenced_sample_rows':len(samples),'sequenced_people':len(times),'patients_table_people':len(people),
            'people_with_two_or_more_samples':sum(len(v)>=2 for v in times.values()),
            'people_with_three_or_more_samples':sum(len(v)>=3 for v in times.values()),
            'serial_people_by_source_category':dict(sorted(Counter(people[p] for p,v in times.items() if len(v)>=2).items())),
            'duplicate_subject_day_coordinates':sum(len(v)-len(set(v)) for v in times.values()),
            'exposure_rows':len(exposures),'exposure_people':len({r['pid'] for r in exposures}),
            'exposure_people_without_sample':len({r['pid'] for r in exposures}-set(times)),
            'unparseable_exposure_time_rows':invalid,'reversed_exposure_intervals':reversed_intervals,
            'prepost_exposure_rows':len(prepost),'people_with_prepost_exposure':len({p for p,_,_ in prepost}),
            'duplicate_person_interval_coordinates':len(prepost)-len(set(prepost)),
            'note':'Rows are not independent courses. Published 79-person analysis matches pair-contributing IDs, while 80 serial subjects occur in sample/patient tables. No taxon values inspected; development-only source.',
            **pair_qc}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('archive',type=Path);p.add_argument('--code-archive',type=Path);args=p.parse_args()
    result=screen(args.archive,code_archive=args.code_archive)
    (Path(__file__).resolve().parents[1]/'results/armord_design.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
