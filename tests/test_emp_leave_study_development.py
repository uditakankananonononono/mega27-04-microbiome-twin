import sys
from pathlib import Path

import pytest


def test_viewed_emp_leave_study_accounting():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
    from emp_leave_study_development import summarize
    out = summarize()
    assert out['candidate_studies'] == 20 and out['scored_studies'] == 16
    assert sum(r['samples'] for r in out['study_results'] if r['status'].startswith('viewed_leave')) == 803
    assert out['covered_samples'] <= 803
    assert all(r['covered_host_labels'] <= r['host_labels'] for r in out['study_results'] if r['status'].startswith('viewed_leave'))
    assert all(r['median_retained_subset_mass_in_train_vocab'] >= .9 for r in out['study_results'] if r['status'].startswith('viewed_leave') and r['covered_samples'] == r['samples'])
    with pytest.raises(ValueError, match='threshold'):
        summarize(0)
