"""Outcome-blind aggregate screen of pinned Meta2DB metadata, not model validation.

Run against the Zenodo v1 metadata CSV after checking its published MD5. No row,
subject identifier, sample value, or abundance profile is copied to results.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_MD5 = 'be523d58a63947765d728f1f4f89b07a'
MISSING = {'', 'not available', 'not applicable', 'na', 'nan', 'none', 'null', 'unknown', 'n/a'}
FIELDS = ('project_name', 'project_id', 'host_subject_id', 'run_acc',
          'days_from_first_collection', 'collection_date', 'antibiotics',
          'antibiotics_family', 'health_disease_stat', 'seq_type')


def summarize(path):
    raw = Path(path).read_bytes()
    if hashlib.md5(raw).hexdigest() != EXPECTED_MD5:
        raise ValueError('Meta2DB v1 metadata MD5 mismatch')
    data = pd.read_csv(path, dtype=str, keep_default_na=False, encoding='latin-1', low_memory=False)
    if set(FIELDS) - set(data.columns) or len(data) != 13897:
        raise ValueError('unexpected Meta2DB metadata schema or row count')
    valid = {c: ~data[c].str.strip().str.lower().isin(MISSING) for c in FIELDS}
    unit_rows = data[valid['host_subject_id'] & valid['project_name']]
    groups = unit_rows.groupby(['project_name', 'host_subject_id'], sort=False).size()
    repeated = groups[groups > 1]
    with_time = data[valid['days_from_first_collection']]
    time_groups = with_time.groupby(['project_name', 'host_subject_id'], sort=False).size()
    time_repeated = time_groups[time_groups > 1]
    by_project = (with_time.groupby('project_name').size().sort_values(ascending=False).to_dict())
    old = pd.read_csv(ROOT / 'data/raw/mgnify/manifest.csv', dtype=str, keep_default_na=False)
    old_projects = {}
    for row in old.itertuples(index=False):
        for project in re.findall(r'PRJ(?:NA|EB|DB)\d+', row.study_name, flags=re.I):
            old_projects.setdefault(project.upper(), set()).add(row.study)
    matched = data[data.project_id.str.upper().isin(old_projects)]
    overlap = [{'project_id': project, 'project_name': name, 'metadata_rows': int(n),
                'old_mgnify_study_ids': sorted(old_projects[project.upper()])}
               for (name, project), n in matched.groupby(['project_name', 'project_id']).size().items()]
    overlap.sort(key=lambda r: (-r['metadata_rows'], r['project_id']))
    time_multi = []
    for name, part in with_time.groupby('project_name'):
        by_subject = part.groupby('host_subject_id')
        varying_day_subject_labels = sum(g.days_from_first_collection.nunique() > 1
                                         for _, g in by_subject)
        true_on_repeated_subject_labels = sum(len(g) > 1 and g.antibiotics.str.upper().eq('TRUE').any()
                                              for _, g in by_subject)
        changing_antibiotic_labels = sum(len(g) > 1 and g.antibiotics.str.upper().nunique() > 1
                                         for _, g in by_subject)
        time_multi.append({'project_name': name, 'time_populated_rows': len(part),
                           'subject_labels': len(by_subject),
                           'subject_labels_with_varying_day': int(varying_day_subject_labels),
                           'repeated_subject_labels_with_any_antibiotics_true': int(true_on_repeated_subject_labels),
                           'repeated_subject_labels_with_changing_antibiotics_flag': int(changing_antibiotic_labels)})
    agp = data[data.project_name == '2022_American_Gut_Project']
    return {'status': 'outcome_blind_composite_metadata_screen_not_external_test',
            'source': 'https://zenodo.org/records/17315984', 'metadata_md5': EXPECTED_MD5,
            'rows': len(data), 'columns': len(data.columns),
            'project_name_labels': data.project_name.nunique(),
            'project_id_labels': data.project_id.nunique(),
            'fields_populated': {c: int(valid[c].sum()) for c in FIELDS},
            'antibiotics_true_rows': int(data.antibiotics.str.strip().str.upper().eq('TRUE').sum()),
            'project_subject_labels': len(groups), 'repeated_project_subject_labels': len(repeated),
            'rows_in_repeated_project_subject_labels': int(repeated.sum()),
            'project_names_with_repeated_subject_labels': repeated.index.get_level_values(0).nunique(),
            'project_names_with_time_values': len(by_project),
            'time_populated_rows_by_project': by_project,
            'time_field_project_design_leads': time_multi,
            'repeated_project_subject_labels_with_time_values': len(time_repeated),
            'overlap_with_old_mgnify_by_embedded_original_project': overlap,
            'overlap_project_count': matched.project_id.nunique(),
            'metadata_rows_in_overlapping_projects': len(matched),
            'agp_project_name_rows': len(agp),
            'agp_project_ids': agp.project_id.value_counts().to_dict(),
            'admitted_independent_studies': 0,
            'note': 'Project-level accession overlap does not establish exact sample identity or non-overlap of remaining projects. Project/subject labels are not audited biological units. Metadata time and antibiotic fields do not establish aligned courses; source-specific rights, assay and outcome eligibility remain unresolved. No abundance outcomes read.'}


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('usage: python scripts/meta2db_metadata_screen.py downloaded_metadata.csv')
    report = summarize(sys.argv[1])
    destination = Path(__file__).resolve().parents[1] / 'results/meta2db_metadata_screen.json'
    destination.write_text(json.dumps(report, indent=2) + '\n')
    print(report['rows'], report['project_name_labels'], report['repeated_project_subject_labels'])
