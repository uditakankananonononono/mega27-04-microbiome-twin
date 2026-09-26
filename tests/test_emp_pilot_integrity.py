"""Verify archived EMP failed-coverage diagnostic cannot be mislabeled win."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_emp_attempt_is_excluded_by_coverage():
    result=json.loads((ROOT/'results/pilot_emp_transfer.json').read_text())
    assert result['status']=='three_study_source_pilot_not_top_tool_win'
    assert result['test_samples']==216 and len(result['test_studies'])==3
    assert result['protocol_sha256']==hashlib.sha256((ROOT/'EMP_PILOT_PROTOCOL.md').read_bytes()).hexdigest()
    assert result['median_vocab_count_mass']<.9 and result['minimum_vocab_count_mass']<.9
    assert all(v['status']=='ok' and len(v['study_metrics'])==3 for v in result['models'].values())
