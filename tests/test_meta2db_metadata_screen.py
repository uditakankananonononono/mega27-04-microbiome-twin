import pytest
from scripts.meta2db_metadata_screen import summarize


def test_metadata_screen_rejects_unpinned_content(tmp_path):
    p = tmp_path / 'metadata.csv'
    p.write_text('project_name,host_subject_id\nfake,one\n')
    with pytest.raises(ValueError, match='MD5 mismatch'):
        summarize(p)
