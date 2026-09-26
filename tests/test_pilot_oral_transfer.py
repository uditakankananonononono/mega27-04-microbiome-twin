"""Lock basic integrity of the archived one-study debug pilot."""
import hashlib,json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def test_pilot_source_hashes_and_people_count():
    result=json.loads((ROOT/'results/pilot_oral_transfer.json').read_text())
    assert result['status']=='one_study_debug_pilot_not_external_win'
    assert result['train_samples']==20 and result['test_sites']==87 and result['test_people']==58
    assert result['protocol_sha256']==hashlib.sha256((ROOT/'PILOT_TRANSFER_PROTOCOL.md').read_bytes()).hexdigest()
    for p,h in result['source_sha256'].items():
        assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
    for model,record in result['models'].items():
        assert record['status']=='ok' and len(record['site_errors'])==87
        assert len(record['person_median_errors'])==58
        assert np.isfinite(list(record['site_errors'].values())).all()
        assert np.isclose(np.mean(list(record['person_median_errors'].values())),
                          record['macro_person_median_bray_curtis'])


def test_full_community_sensitivity_has_no_win_claim():
    result=json.loads((ROOT/'results/pilot_oral_sensitivity.json').read_text())
    assert result['status']=='secondary_sensitivity_not_external_win'
    assert result['coverage_rejected_sites']==['SRS281291']
    assert all(v['n_gated_people']==57 for v in result['models'].values())
