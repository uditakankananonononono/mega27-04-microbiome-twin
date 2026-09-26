"""End-to-end validation of predict-calibrated on six archived cNODE tables.

Same-dataset, already-viewed data. No subjects/source family metadata or
independent external validation; generated IDs/Taxon_N columns are positional.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from microtwin.conformal import bray_radius
from microtwin.data import DATASETS, bray_curtis, load
from microtwin.local_calibrated_predict import predict_with_radius
from microtwin.models import PresenceMean


def evaluate(name, seed=0):
    if name not in DATASETS:
        raise ValueError('unknown dataset')
    z,p=load(name)
    source=ROOT/'data/raw/cnode'/f'{name}.csv'
    source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    ix=np.random.default_rng(seed).permutation(len(z))
    ntrain=int(.6*len(z));ncal=int(.2*len(z))
    tr,cal,te=ix[:ntrain],ix[ntrain:ntrain+ncal],ix[ntrain+ncal:]
    # Input-only coverage gate: refuse unseen present taxa, then score only
    # the non-abstained calibration/query rows. This post-hoc diagnostic is
    # not the unconditional 60/20/20 estimand in internal_conformal_check.
    known=p[tr].sum(0)>0
    cal_ok=~(p[cal][:,~known]>0).any(axis=1)
    te_ok=~(p[te][:,~known]>0).any(axis=1)
    raw_cal,raw_te=len(cal),len(te)
    cal,te=cal[cal_ok],te[te_ok]
    taxa=[f'Taxon_{i:03d}' for i in range(p.shape[1])]
    def frame(values, rows):
        out=pd.DataFrame(values,columns=taxa)
        out.insert(0,'sample_id',[f'sample_{j}' for j in rows])
        return out
    with TemporaryDirectory() as td:
        d=Path(td)
        train,calibration,query=[d/n for n in ('train.tsv','cal.tsv','query.tsv')]
        frame(p[tr],tr).to_csv(train,sep='\t',index=False,float_format='%.17g')
        frame(p[cal],cal).to_csv(calibration,sep='\t',index=False,float_format='%.17g')
        frame((p[te]>0).astype(int),te).to_csv(query,sep='\t',index=False)
        pred,report=predict_with_radius(train,calibration,query,unit='relative_abundance',
                                        source_id=f'cNODE-archived-{name}',processing_authorized=True)
        if report['train_samples']!=len(tr) or report['calibration_samples']!=len(cal) or report['query_samples']!=len(te):
            raise ValueError('split accounting mismatch')
        cli_pred=pred[taxa].to_numpy(float)
        frozen=PresenceMean().fit(z[tr],p[tr])
        expected=frozen.predict(z[te])
        if not np.allclose(cli_pred,expected,atol=1e-12):
            raise ValueError('local calibrated predictor disagrees with archived PresenceMean')
        calerr=bray_curtis(frozen.predict(z[cal]),p[cal])
        radius=bray_radius(calerr,.1)['radius']
        if not np.isclose(radius,report['uncertainty']['radius'],atol=1e-12):
            raise ValueError('radius disagrees with independent implementation')
        testerr=bray_curtis(cli_pred,p[te])
    if hashlib.sha256(source.read_bytes()).hexdigest()!=source_hash:
        raise ValueError('source changed during run')
    return {'dataset':name,'raw_source_sha256':source_hash,'train':len(tr),
            'calibration_candidates':raw_cal,'test_candidates':raw_te,
            'calibration_abstained_unknown_present_taxa':raw_cal-len(cal),
            'test_abstained_unknown_present_taxa':raw_te-len(te),
            'calibration':len(cal),'test':len(te),'radius':radius,
            'vacuous':report['uncertainty']['vacuous'],
            'test_covered':int(np.sum(testerr<=radius)),
            'empirical_coverage':float(np.mean(testerr<=radius)),
            'max_prediction_difference_vs_archived_presence_mean':float(np.max(np.abs(cli_pred-expected)))}


if __name__=='__main__':
    rows=[evaluate(d) for d in DATASETS]
    out={'status':'internal_same_dataset_real_data_cli_validation_not_external_reliability',
         'split_seed':0,'nominal_coverage':.9,'datasets':rows,
         'note':'Actual predict-calibrated path on a 60/20/20 candidate split after assemblage dedup, then input-only abstention on unseen present taxa. Coverage conditional on eligible rows is a different estimand from the unconditional internal_conformal_check. Already-viewed six cNODE tables; no subject/source-family exchangeability proof, no TRI, no cross-source or clinical coverage guarantee.'}
    (ROOT/'results/local_calibrated_six_dataset_check.json').write_text(json.dumps(out,indent=2)+'\n')
    for r in rows:
        print(r['dataset'],r['test_covered'],r['test'],r['radius'],r['max_prediction_difference_vs_archived_presence_mean'])
