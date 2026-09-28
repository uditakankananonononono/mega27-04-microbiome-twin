"""Frozen toy panel only; not empirical detection statistics."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from microtwin.ambiguity_certificate import certify_three_species_removal
PANEL={'straddling':(-.4,.4),'positive':(.1,.4),'negative':(-.4,-.1),'zero_bound':(0,.4),'point_zero':(0,0)}
if __name__=='__main__':
    rows=[{'case':name,**certify_three_species_removal(*bounds)} for name,bounds in PANEL.items()]
    d={'protocol':'results/PREREG_20260928_counterfactual_ambiguity_certificate.md',
       'panel':rows,'certificate_positive':sum(r['status']=='opposite_sign_witness' for r in rows),
       'generic_free_parameter_flag_positive':sum(r['generic_free_parameter_flag'] for r in rows),
       'note':'Five deliberately chosen analytic toy intervals; counts do not estimate real-world detection accuracy.'}
    out=ROOT/'results/ambiguity_certificate_toy_check.json';out.write_text(json.dumps(d,indent=2)+'\n')
    print(out, 'certificate',d['certificate_positive'],'generic',d['generic_free_parameter_flag_positive'])
