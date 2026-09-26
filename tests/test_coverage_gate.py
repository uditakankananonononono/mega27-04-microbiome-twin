from microtwin.coverage_gate import coverage_gate


def test_coverage_gate_abstains_on_rare_outlier():
    r=coverage_gate({'shared_genera':100,'minimum_test_mass_covered':.89})
    assert not r['eligible_on_vocabulary_only']
    assert r['reasons']==['low_sample_vocabulary_coverage']


def test_coverage_gate_only_vocabulary_check():
    r=coverage_gate({'shared_genera':20,'minimum_test_mass_covered':.9})
    assert r['eligible_on_vocabulary_only']
    assert 'does not verify labels' in r['note']
