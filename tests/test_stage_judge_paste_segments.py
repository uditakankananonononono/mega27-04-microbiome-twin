import hashlib
from pathlib import Path
import sys

import pytest


def test_retired_old_paper_staging_rejected(tmp_path):
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/'scripts'))
    from stage_judge_paste_segments import stage
    with pytest.raises(ValueError, match='retired manuscript staging'):
        stage(tmp_path)
