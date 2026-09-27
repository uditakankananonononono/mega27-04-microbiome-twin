from pathlib import Path
import json
import sys


def test_mgnify_family_sensitivity_reproduces_and_preserves_units():
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/'scripts'))
    from mgnify_family_sensitivity import run
    observed=run()
    stored=json.loads((root/'results/mgnify_family_sensitivity.json').read_text())
    assert observed == stored
    assert observed['original']['rows']==160
    assert observed['single_token_rows']+observed['unresolved_rows']==160
    assert observed['lexical_one_per_family']['rows']==observed['provisional_families']
    assert observed['repeated_families']==1
    assert observed['repeated_family_details'][0]['family']=='PRJNA715245'
    assert observed['repeated_family_details'][0]['win_status_discordant']
