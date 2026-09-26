from pathlib import Path
import sys


def test_emp_within_study_baseline_abstains_nonindependent_subjects():
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/'scripts'))
    from emp_within_study_baseline import summarize
    r=summarize()
    assert r['candidate_studies']==20
    assert r['scored_studies']==16
    assert any(v['status']=='abstained_fewer_than_ten_subjects' for v in r['study_results'])
    assert all(v['subjects']>=10 for v in r['study_results'] if v['status'].startswith('within_study'))


def test_emp_metadata_hash_guard_precedes_scoring(tmp_path, monkeypatch):
    import emp_within_study_baseline as mod
    bad=tmp_path/'metadata.tsv';bad.write_text('changed')
    monkeypatch.setattr(mod,'META',bad)
    import pytest
    with pytest.raises(ValueError,match='metadata checksum mismatch'):mod.summarize()
