from scripts.mdsine_dual_mouse_summary import summarize

def test_mouse_level_diagnostic_reports_original_mouse_units():
    healthy=summarize('healthy');uc=summarize('uc')
    assert healthy['n_mice']==4 and uc['n_mice']==5
    for result in [healthy,uc]:
        for endpoint in result['endpoints'].values():
            assert endpoint['baseline_higher_mice']+endpoint['baseline_lower_mice']+endpoint['baseline_equal_mice']==result['n_mice']
        assert result['endpoints']['balanced_accuracy']['baseline_higher_mice']==result['n_mice']
        assert result['endpoints']['sensitivity']['baseline_lower_mice']==result['n_mice']
    assert healthy['endpoints']['pair_median_conditional_rmse']['baseline_lower_mice']==3
    assert uc['endpoints']['pair_median_conditional_rmse']['baseline_lower_mice']==5
