import sys
from pathlib import Path

import numpy as np


def test_assemblage_novelty_reproducible_and_grouped():
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/'scripts'))
    from oral_pilot_assemblage_novelty import summarize
    x=summarize(resamples=1000)
    assert x==summarize(resamples=1000)
    assert x['people']==58 and x['test_sites']==87
    assert x['high_novelty_people']+x['low_or_equal_novelty_people']==58
    assert len(x['pilot_sha256'])==64 and len(x['subject_map_sha256'])==64
    assert np.isclose(x['models']['graphtwin']['high_minus_low_model_advantage_gap'], -0.009444714440504483)
    assert x['median_person_taxon_richness_high_novelty'] < x['median_person_taxon_richness_low_or_equal_novelty']
    assert -0.5 < x['pearson_novelty_taxon_richness'] < -0.45
    assert x['models']['graphtwin']['bootstrap95_linear_novelty_slope_adjusted_for_taxon_richness'][1] > 0
