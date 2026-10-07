"""Aggregate-only source admission. Importing never accesses network or writes files."""
import collections
import io
import json
import math
import time
import xml.etree.ElementTree as E
import requests


def summarize(buf, expected_samples):
    rows=0;ids=collections.Counter();subjects={};missing=collections.Counter();phases=collections.Counter();arms=collections.Counter();sems=collections.Counter();years=collections.Counter();presence=collections.Counter();numeric=collections.Counter();
    for ev,el in E.iterparse(buf,events=('end',)):
     if el.tag!='SAMPLE':continue
     rows+=1
     attrs={x.findtext('TAG'):x.findtext('VALUE') for x in el.iter('SAMPLE_ATTRIBUTE')}
     ids[el.get('accession','')]+=1
     for field in ['host_subject_id','status','supplement','semester','collection_date']:
      if not attrs.get(field):missing[field]+=1
     subj=attrs.get('host_subject_id');phase=attrs.get('status');arm=attrs.get('supplement');sem=attrs.get('semester');dt=attrs.get('collection_date') or ''
     phases[phase]+=1;arms[arm]+=1;sems[sem]+=1;years[dt[:4]]+=1
     if subj:
      rec=subjects.setdefault(subj,{'phases':collections.Counter(),'arms':set(),'semesters':set()});rec['phases'][phase]+=1;rec['arms'].add(arm);rec['semesters'].add(sem)
     for field in ['acetate','propionate','butyrate','total SCFA']:
      value=attrs.pop(field,None)
      if value is not None and value.strip():
       presence[field]+=1
       try:
        if math.isfinite(float(value)):numeric[field]+=1
       except ValueError:pass
      value=None
     attrs.clear();el.clear()
    assert rows==expected_samples and len(ids)==expected_samples, "Unreconciled SAMPLE inventory"
    out={'sample_count':rows,'unique_sample_accessions':len(ids),'duplicate_sample_accessions':sum(n-1 for n in ids.values()),'subject_keys':len(subjects),'missing_metadata_counts':dict(missing),'phase_counts':dict(phases),'arm_counts':dict(arms),'semester_counts':dict(sems),'collection_year_counts':dict(years),'outcome_present_counts':dict(presence),'outcome_numeric_parseable_counts':dict(numeric),'subjects_with_both_phases_ge1':sum(all(v['phases'][p]>=1 for p in ['before','during']) for v in subjects.values()),'subjects_with_both_phases_ge3':sum(all(v['phases'][p]>=3 for p in ['before','during']) for v in subjects.values()),'subjects_multiple_arms':sum(len(v['arms'])>1 for v in subjects.values()),'subjects_multiple_semesters':sum(len(v['semesters'])>1 for v in subjects.values()),'independent_validation':False,'outcomes_retained':False}
    subjects.clear()
    return out

def run():
    start=time.monotonic()
    url='https://www.ebi.ac.uk/ena/browser/api/xml/search'
    params={'result':'sample','query':'study_accession="PRJNA428736"','limit':0}
    with requests.get(url,params=params,stream=True,timeout=(10,50)) as response:
        response.raise_for_status()
        with io.BytesIO() as buf:
            for chunk in response.iter_content(65536):
                if time.monotonic()-start>60:
                    raise RuntimeError('60 second cap')
                if buf.tell()+len(chunk)>20*1024*1024:
                    raise RuntimeError('20MB cap')
                buf.write(chunk)
            bytecount=buf.tell()
            buf.seek(0)
            result=summarize(buf,1201)
        result.update(source=response.url,byte_count=bytecount,seconds=round(time.monotonic()-start,3))
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    run()
