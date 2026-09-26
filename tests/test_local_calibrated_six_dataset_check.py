import sys
from pathlib import Path


def test_real_endpoint_abstention_and_reference_equivalence():
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/'scripts'))
    from local_calibrated_six_dataset_check import evaluate
    gut=evaluate('Human_Gut')
    assert gut['train']+gut['calibration_candidates']+gut['test_candidates']==106
    assert gut['calibration_abstained_unknown_present_taxa']==0
    assert gut['test_abstained_unknown_present_taxa']==0
    assert gut['test_covered']==19 and gut['test']==22
    assert gut['max_prediction_difference_vs_archived_presence_mean']<1e-12
    oral=evaluate('Human_Oral')
    assert oral['calibration_abstained_unknown_present_taxa']==2
    assert oral['test_abstained_unknown_present_taxa']==2
    assert oral['test_covered']==27 and oral['test']==28
    assert oral['max_prediction_difference_vs_archived_presence_mean']<1e-12
