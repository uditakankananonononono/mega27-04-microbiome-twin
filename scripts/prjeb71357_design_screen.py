"""Outcome-blind ENA run metadata screen for a probiotic-adjunct study.

Only project run/sample/title/strategy fields are consumed. Person and run IDs
are transient; output is aggregate and does not certify treatment-arm labels.
"""
import csv
import hashlib
import io
import json
import re
from collections import Counter,defaultdict
from pathlib import Path

EXPECTED='348cccfc34bb2873a76445c2141c9499ea16d3e193c22ee570ba3a4fc4a82d2a'
TITLE=re.compile(r'F(\d+)(BL|EP|MP)\Z')
FIELDS={'run_accession','sample_accession','sample_title','study_accession','library_strategy'}

def screen(path, expected_sha=EXPECTED):
    if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=expected_sha:raise ValueError('source metadata checksum mismatch')
    rows=list(csv.DictReader(io.StringIO(Path(path).read_text(encoding='utf-8')),delimiter='\t'))
    if not rows or set(rows[0])!=FIELDS:raise ValueError('unexpected ENA header')
    if any(r['study_accession']!='PRJEB71357' for r in rows):raise ValueError('wrong study accession')
    if len({r['run_accession'] for r in rows})!=len(rows) or len({r['sample_accession'] for r in rows})!=len(rows):raise ValueError('duplicate run or sample')
    by=defaultdict(set)
    for r in rows:
        m=TITLE.fullmatch(r['sample_title'])
        if m is None:raise ValueError('unparseable sample title')
        if m.group(2) in by[m.group(1)]:raise ValueError('duplicate person phase')
        by[m.group(1)].add(m.group(2))
    phase_counts=Counter(phase for phases in by.values() for phase in phases)
    return {'status':'ENA_run_header_only_no_abundance_or_arm_labels','source_tsv_sha256':expected_sha,
            'run_rows':len(rows),'unique_sample_accessions':len({r['sample_accession'] for r in rows}),
            'library_strategies':dict(sorted(Counter(r['library_strategy'] for r in rows).items())),
            'subject_prefixes':len(by),'phase_counts':dict(sorted(phase_counts.items())),
            'subjects_with_all_three_phase_titles':sum(len(s)==3 for s in by.values()),
            'subjects_with_baseline_and_endpoint_titles':sum({'BL','EP'}<=s for s in by.values()),
            'subjects_missing_at_least_one_phase':sum(len(s)<3 for s in by.values()),
            'note':'BL/EP/MP title interpretation inferred from paper timing, not yet cross-checked with depositors. Arm mapping absent. Not certified independent final test; no taxon data read.'}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('metadata',type=Path);args=p.parse_args()
    x=screen(args.metadata)
    (Path(__file__).resolve().parents[1]/'results/prjeb71357_design.json').write_text(json.dumps(x,indent=2)+'\n')
    print(json.dumps(x,indent=2))
