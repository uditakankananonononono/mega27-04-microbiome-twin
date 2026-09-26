import pytest
from scripts.meta2db_metadata_screen import summarize


def test_metadata_screen_rejects_unpinned_content(tmp_path):
    p = tmp_path / 'metadata.csv'
    p.write_text('project_name,host_subject_id\nfake,one\n')
    with pytest.raises(ValueError, match='MD5 mismatch'):
        summarize(p)


def test_pinned_metadata_crosswalk_when_available():
    from pathlib import Path
    p = Path('/tmp/meta2db_metadata.csv')
    if not p.exists():
        pytest.skip('pinned source CSV not in local scratch')
    r = summarize(p)
    assert r['overlap_project_count'] == 7
    assert r['metadata_rows_in_overlapping_projects'] == 2038
    assert {v['project_id'] for v in r['overlap_with_old_mgnify_by_embedded_original_project']} == {
        'PRJNA834801', 'PRJEB11419', 'PRJNA385949', 'PRJEB47976',
        'PRJEB21612', 'PRJNA433459', 'PRJNA547717'}
