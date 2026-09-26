import hashlib
from pathlib import Path
import sys

import pytest


def test_staging_complete_and_repeatable(tmp_path):
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/'scripts'))
    from stage_judge_paste_segments import stage
    first=stage(tmp_path)
    assert first['status']=='staged_not_submitted'
    assert first['segment_count']==86
    assert len(first['segments'])==86
    assert first['part_13_resume_sha256']==hashlib.sha256((tmp_path/'013.txt').read_bytes()).hexdigest()
    assert stage(tmp_path)==first
    (tmp_path/'013.txt').write_text('corrupt')
    with pytest.raises(ValueError,match='differs'):stage(tmp_path)
