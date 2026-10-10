"""Compute paired local composition losses; do not authenticate holdout status."""
import csv
import io
import hashlib
from pathlib import Path
import numpy as np
from .data import bray_curtis


def _bytes(path):
    p=Path(path)
    if not p.is_file() or p.is_symlink() or p.suffix not in ('.csv','.tsv') or p.stat().st_size>10_000_000:
        raise ValueError('regular CSV/TSV file required, maximum 10 MB')
    return p,p.read_bytes()


def _composition(raw,suffix):
    delimiter=',' if suffix=='.csv' else '\t'
    try: rows=list(csv.reader(io.StringIO(raw.decode('utf-8')),delimiter=delimiter,strict=True))
    except (UnicodeError,csv.Error) as e:raise ValueError('well-formed UTF-8 composition table required') from e
    if not rows or len(rows[0])<2 or rows[0][0]!='sample_id' or len(set(rows[0]))!=len(rows[0]):
        raise ValueError('sample_id followed by unique taxa required')
    if len(rows)<2 or len(rows)>10001 or len(rows[0])>1001:
        raise ValueError('1-10000 samples and 1-1000 taxa required')
    if any(len(r)!=len(rows[0]) for r in rows[1:]):raise ValueError('ragged table')
    ids=[r[0] for r in rows[1:]];taxa=rows[0][1:]
    if any(not s or s!=s.strip() for s in ids+taxa) or len(set(ids))!=len(ids):
        raise ValueError('exact nonempty trimmed unique sample/taxon labels required')
    try:x=np.asarray([r[1:] for r in rows[1:]],dtype=float)
    except (TypeError,ValueError) as e:raise ValueError('numeric composition entries required') from e
    if not np.isfinite(x).all() or (x<0).any() or not np.allclose(x.sum(1),1,rtol=0,atol=1e-6):
        raise ValueError('finite nonnegative relative compositions summing to one required; no implicit normalization')
    return ids,taxa,x


def paired_prediction_losses(truth, predictions, labels):
    """Strict row/taxon order alignment, no silent intersection or normalization.

    Label CSV: sample_id,subject_id,source_family. A subject label cannot span
    families within this partition. No claim of disjoint training follows.
    Output is private intermediate data (labels and per-row losses).
    """
    if not isinstance(predictions,dict) or not 2<=len(predictions)<=20 or any(not isinstance(k,str) or not k or k!=k.strip() for k in predictions):
        raise ValueError('2-20 named model prediction files required')
    loaded={}; hashes={}; paths={}
    for role,path in [('truth',truth),('labels',labels)]+[('prediction:'+k,v) for k,v in predictions.items()]:
        p,raw=_bytes(path);loaded[role]=raw;paths[role]=p;hashes[role]=hashlib.sha256(raw).hexdigest()
    ids,taxa,y=_composition(loaded['truth'],paths['truth'].suffix)
    if paths['labels'].suffix!='.csv':raise ValueError('label map must be CSV')
    try:rows=list(csv.reader(io.StringIO(loaded['labels'].decode('utf-8')),strict=True))
    except (UnicodeError,csv.Error) as e:raise ValueError('well-formed UTF-8 label map required') from e
    if not rows or rows[0]!=['sample_id','subject_id','source_family'] or len(rows)!=len(ids)+1 or any(len(r)!=3 for r in rows[1:]):
        raise ValueError('exact sample_id,subject_id,source_family label map required')
    if [r[0] for r in rows[1:]]!=ids or any(not v or v!=v.strip() for r in rows[1:] for v in r):
        raise ValueError('label map exact row order and nonempty trimmed values required')
    subject_families={}
    for _,subject,family in rows[1:]:
        if subject in subject_families and subject_families[subject]!=family:
            raise ValueError('submitted subject appears in multiple source families')
        subject_families[subject]=family
    errors={}
    for name in predictions:
        key='prediction:'+name
        pids,ptaxa,p=_composition(loaded[key],paths[key].suffix)
        if pids!=ids or ptaxa!=taxa:
            raise ValueError('all model rows and taxon order must exactly match truth')
        errors[name]=bray_curtis(p,y).tolist()
    if any(p.read_bytes()!=loaded[k] for k,p in paths.items()):raise ValueError('inputs changed during evaluation')
    return {'loss_input':{'errors':errors,'families':[r[2] for r in rows[1:]]},
            'provenance':{'status':'local_paired_loss_computation_only','n_samples':len(ids),'n_taxa':len(taxa),
                          'n_subject_labels':len(subject_families),'metric':'Bray-Curtis on submitted relative compositions',
                          'input_sha256':hashes,'external_win_certified':False,
                          'limitations':['Private intermediate contains submitted family labels and row-level errors.',
                                         'No training/holdout, subject independence, rights, assay or budget verification.',
                                         'Predictions are supplied, not fitted by this evaluator.']}}
