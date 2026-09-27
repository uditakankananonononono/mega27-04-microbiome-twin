"""Deterministically stage safe-size, numbered manuscript paste segments.

No browser or ChatGPT submission occurs here. The PDF extraction and every
committed chunk are checked before staging; restart at the first unsent segment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
PREP=ROOT/'judge/paste-prep-01'


def stage(outdir, *, max_chars=3300):
    if not isinstance(max_chars,int) or not 1000 <= max_chars <= 4000:
        raise ValueError('max_chars must be an integer in 1000..4000')
    manifest=json.loads((PREP/'manifest.json').read_text())
    if manifest.get('status','').startswith('retired_'):
        raise ValueError('retired manuscript staging: regenerate from current authorless edition')
    pdf=ROOT/manifest['paper_path']
    raw=pdf.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=manifest['paper_sha256']:
        raise ValueError('source PDF hash mismatch')
    extraction=subprocess.check_output(['pdftotext','-layout',str(pdf),'-'])
    if hashlib.sha256(extraction).hexdigest()!=manifest['extraction_sha256']:
        raise ValueError('paper extraction hash mismatch')
    chunk_text=[]
    for i, entry in enumerate(manifest['chunks'],1):
        text=(PREP/f'chunk-{i:02}.txt').read_text()
        if hashlib.sha256(text.encode()).hexdigest()!=entry['sha256']:
            raise ValueError(f'chunk {i} hash mismatch')
        chunk_text.append(text)
    # The chunk envelope has page labels, while every PDF page body is intact.
    assembled=''.join(chunk_text)
    page_bodies=extraction.decode().split('\x0c')[:-1]
    for i, body in enumerate(page_bodies,1):
        marker=f'[[PAPER PAGE {i}]]\n'
        if assembled.count(marker)!=1:
            raise ValueError(f'PDF page {i} marker missing or duplicated')
        start=assembled.index(marker)+len(marker)
        end=assembled.find('[[PAPER PAGE ',start)
        envelope=assembled[start:] if end<0 else assembled[start:end]
        if envelope.strip()!=body.strip():
            raise ValueError(f'PDF page {i} text mismatch in prepared chunks')
    out=Path(outdir)
    out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for ci,chunk in enumerate(chunk_text,1):
        count=(len(chunk)+max_chars-1)//max_chars
        for j in range(count):
            n=len(rows)+1
            text=(f'[ARCHIVED PAPER SUBMISSION {n}; original chunk {ci}/30; segment {j+1}/{count}]\n'
                  +chunk[j*max_chars:(j+1)*max_chars]+'\n[END SEGMENT]')
            path=out/f'{n:03}.txt'
            if path.exists() and path.read_text()!=text:
                raise ValueError(f'existing staged segment differs: {path}')
            path.write_text(text)
            rows.append({'number':n,'chunk':ci,'segment':j+1,'sha256':hashlib.sha256(text.encode()).hexdigest(),
                         'characters':len(text),'file':path.name})
    result={'status':'staged_not_submitted','pdf_sha256':manifest['paper_sha256'],
            'extraction_sha256':manifest['extraction_sha256'],'segment_count':len(rows),
            'part_13_resume_sha256':rows[12]['sha256'],'segments':rows}
    (out/'staging_manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--out',default=str(ROOT/'judge/paste-prep-01/segments-3300'))
    args=p.parse_args()
    r=stage(args.out)
    print(f"staged {r['segment_count']} segments; resume at 013, sha256 {r['part_13_resume_sha256']}; no submission")
