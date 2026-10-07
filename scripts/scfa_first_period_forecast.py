"""Private local inputs; aggregate-only first-period SCFA result."""
from pathlib import Path
import argparse
import hashlib
import json
import time
import signal
import openpyxl
from microtwin.scfa_forecast import prepare, evaluate


def load(path):
    w=openpyxl.load_workbook(path,read_only=True,data_only=True)
    s=w.active;s.reset_dimensions();it=s.iter_rows(values_only=True);header=next(it)
    if len(set(header))!=len(header):raise ValueError('duplicate header')
    try:
        return [dict(zip(header,row)) for row in it if any(v is not None for v in row)]
    finally:
        w.close()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--metadata',required=True)
    parser.add_argument('--assay',required=True);parser.add_argument('--out',required=True)
    a=parser.parse_args();start=time.monotonic()
    def timeout(*_):raise TimeoutError('frozen evaluation wall cap reached')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(120)
    mp,ap=Path(a.metadata),Path(a.assay);dest=Path(a.out)
    if dest.exists():raise ValueError('output already exists')
    mh=hashlib.sha256(mp.read_bytes()).hexdigest();am=hashlib.md5(ap.read_bytes()).hexdigest()
    if mh!='5395f5bb54d50cd64459f2cb77ef40af0b4edfd51ba4a804e8bf09fa14897942' or am!='0198c9ca3134d8829ee7de71a9b0a3c0':
        raise ValueError('source bytes do not match frozen hashes')
    ids,g,x,y,screen=prepare(load(mp),load(ap))
    result={'screen':screen,'source':'https://zenodo.org/records/15363886',
            'license':'CC BY 4.0 (this deposit only)',
            'metadata_sha256':mh,'assay_md5':am,
            'protocol_sha256':hashlib.sha256(Path('results/PREREG_20261007_scfa_first_period_forecast.md').read_bytes()).hexdigest(),
            'outcome':'not_evaluable_no_fits' if not screen['evaluable'] else 'evaluated'}
    if screen['evaluable']:result['evaluation']=evaluate(ids,g,x,y)
    result['elapsed_seconds']=round(time.monotonic()-start,3)
    result['participant_rows_published']=False
    with dest.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    signal.alarm(0)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
