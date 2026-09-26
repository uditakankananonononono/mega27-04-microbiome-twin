"""Outcome-blind DIABIMMUNE 16S/event metadata screen.

Only matrix header IDs and event-subject/time fields are read. Re-fetch the
original public .xls and matrix, verify source bytes and convert to a temporary
XLSX. LibreOffice ZIP metadata is nondeterministic, so do not pin XLSX bytes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/source_family_candidates/DIABIMMUNE'
MATRIX = BASE / 'otu_table.filtered.2Maaslin.txt'
SUPPLEMENT = BASE / 'aad0917.SuppTable1.xls'
EXPECTED_MATRIX = 'f202686dd96f1c6c1ec9f2b6e8c70ff0f7da655cc2697e6d91998442bf7b35bc'
EXPECTED_XLS = '2f6276405ffbef98dcbe84d1113ca94e960ebd8dbc35e80ed867a4e8bcf0b191'


def convert_xls(source: Path, directory: Path) -> Path:
    profile = directory / 'lo-profile'
    completed = subprocess.run(
        ['libreoffice', f'-env:UserInstallation={profile.as_uri()}',
         '--headless', '--convert-to', 'xlsx', '--outdir', str(directory), str(source)],
        capture_output=True, text=True, check=True, timeout=60,
    )
    target = directory / (source.stem + '.xlsx')
    if not target.is_file():
        raise ValueError('conversion did not produce XLSX: ' + completed.stdout + completed.stderr)
    return target


def screen(matrix: Path = MATRIX, supplement: Path = SUPPLEMENT):
    import openpyxl  # metadata-screen dependency; not needed by core forecaster
    if hashlib.sha256(matrix.read_bytes()).hexdigest() != EXPECTED_MATRIX:
        raise ValueError('OTU table checksum mismatch')
    if hashlib.sha256(supplement.read_bytes()).hexdigest() != EXPECTED_XLS:
        raise ValueError('original XLS supplement checksum mismatch')
    with matrix.open() as f:
        header = next(csv.reader(f, delimiter='\t'))
    if header[0] != 'sample' or len(header) != len(set(header)):
        raise ValueError('invalid matrix header')
    ages = defaultdict(list)
    for s in header[1:]:
        try:
            p, a = s.split('_', 1)
            ages[p].append(float(a))
        except (ValueError, TypeError):
            raise ValueError('unparseable sample age') from None
    with tempfile.TemporaryDirectory() as tmp:
        book = openpyxl.load_workbook(convert_xls(supplement, Path(tmp)), read_only=True, data_only=True)
        try:
            general_sheet, event_sheet = book['General'], book['Antibiotics']
            general_rows, event_rows = general_sheet.values, event_sheet.values
            if next(general_rows)[0] != 'subject' or tuple(next(event_rows)[:2]) != ('Subject', 'Age (months)'):
                raise ValueError('unexpected clinical sheet headers')
            general = [r[0] for r in general_rows if r[0]]
            if len(general) != len(set(general)):
                raise ValueError('duplicate general subject')
            events = [(r[0], float(r[1])) for r in event_rows
                      if r[0] and isinstance(r[1], (int, float))]
        finally:
            book.close()
    event_subjects = {p for p, _ in events}
    event_prepost = 0
    people_prepost = set()
    for p, t in events:
        if p in ages and any(a < t for a in ages[p]) and any(a > t for a in ages[p]):
            event_prepost += 1
            people_prepost.add(p)
    return {
        'status': 'metadata_header_screen_only_no_model_outcomes',
        'matrix_sha256': EXPECTED_MATRIX, 'original_supplement_sha256': EXPECTED_XLS,
        'matrix_columns': len(header)-1, 'matrix_subject_prefixes': len(ages),
        'supplement_general_subjects': len(general),
        'general_matrix_overlap_subjects': len(set(ages) & set(general)),
        'matrix_only_subject_prefixes': len(set(ages) - set(general)),
        'general_only_subjects': len(set(general) - set(ages)),
        'antibiotic_event_rows': len(events), 'antibiotic_event_subjects': len(event_subjects),
        'antibiotic_event_subjects_with_matrix': len(event_subjects & set(ages)),
        'antibiotic_event_subjects_absent_general': len(event_subjects - set(general)),
        'duplicate_subject_age_event_coordinates': sum(n - 1 for n in Counter(events).values()),
        'event_rows_with_any_prepost_matrix_samples': event_prepost,
        'subjects_with_any_prepost_event': len(people_prepost),
        'note': 'Repeated antibiotic event rows are not independent courses. Infant development confounds time changes. Sample identity and rights unresolved. Matrix abundances not read; development-only source.'
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--matrix', type=Path, default=MATRIX)
    parser.add_argument('--supplement', type=Path, default=SUPPLEMENT)
    args = parser.parse_args()
    out = screen(args.matrix, args.supplement)
    (ROOT / 'results/diabimmune_design.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
