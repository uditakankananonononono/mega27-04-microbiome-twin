import pytest

from microtwin.coverage_gate import coverage_gate


def test_coverage_gate_abstains_on_rare_outlier():
    r=coverage_gate({'shared_genera':100,'minimum_test_mass_covered':.89})
    assert not r['eligible_on_vocabulary_only']
    assert r['reasons']==['low_sample_vocabulary_coverage']


def test_coverage_gate_only_vocabulary_check():
    r=coverage_gate({'shared_genera':20,'minimum_test_mass_covered':.9})
    assert r['eligible_on_vocabulary_only']
    assert 'does not verify labels' in r['note']


def test_invalid_coverage_and_thresholds_fail_closed():
    for bad in (float('nan'), float('inf'), True, '0.9'):
        with pytest.raises(ValueError, match='validated'):
            coverage_gate({'shared_genera': 20, 'minimum_test_mass_covered': bad})
    for bad in (float('nan'), float('inf'), True, '0.9'):
        with pytest.raises(ValueError, match='thresholds'):
            coverage_gate({'shared_genera': 20, 'minimum_test_mass_covered': .9}, min_mass=bad)
    with pytest.raises(ValueError, match='validated'):
        coverage_gate({'shared_genera': True, 'minimum_test_mass_covered': .9})
    with pytest.raises(ValueError, match='thresholds'):
        coverage_gate({'shared_genera': 20, 'minimum_test_mass_covered': .9}, min_shared_genera=True)
