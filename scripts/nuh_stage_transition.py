import sys,json,hashlib
from pathlib import Path
import pandas as pd,numpy as np
from scipy.spatial.distance import cdist
p=Path(sys.argv[1]);out=Path(sys.argv[2]);d=pd.read_csv(p,sep='\t');cols=[c for c in d if '|s__' in c and '|t__' not in c];X=d[cols].to_numpy(float);assert np.isfinite(X).all() and (X>=0).all();X=X/X.sum(axis=1,keepdims=True)
rows=[]
for subject,ix in d.groupby('PatientID').groups.items():
 sub=d.loc[ix];pre=sub[sub.TimePoint=='PRE'];dur=sub[sub.TimePoint=='DURING'];assert len(pre)==len(dur)==1 and sub.Group.nunique()==1
 i=pre.index[0];j=dur.index[0];rows.append((str(subject),sub.Group.iloc[0],X[i],X[j]-X[i]))
rows.sort(key=lambda x:x[0]);summ=[];common=[]
for subject,group,x,truth in rows:
 train=[r for r in rows if r[0]!=subject and r[1]==group];assert len(train)>=3
 distance=cdist(x[None,:],np.array([r[2] for r in train]),metric='braycurtis')[0];order=sorted(range(len(train)),key=lambda k:(distance[k],train[k][0]))[:3]
 predictions={}
 for name,donors in [('group_median',train),('nearest3',[train[k] for k in order])]:
  pred=np.median(np.array([r[3] for r in donors]),axis=0);eligible=abs(truth)>=.001;scored=eligible&(abs(pred)>1e-12)
  predictions[name]=pred
  summ.append(dict(subject=subject,group=group,method=name,eligible=int(eligible.sum()),scored=int(scored.sum()),accuracy=float((np.sign(pred[scored])==np.sign(truth[scored])).mean()) if scored.any() else None,coverage=float(scored.sum()/eligible.sum()) if eligible.any() else None))
 keep=(abs(truth)>=.001)&(abs(predictions['group_median'])>1e-12)&(abs(predictions['nearest3'])>1e-12)
 if keep.any():
  common.append(float(np.mean(np.sign(predictions['nearest3'][keep])==np.sign(truth[keep]))-np.mean(np.sign(predictions['group_median'][keep])==np.sign(truth[keep]))))
s=pd.DataFrame(summ);a=s.pivot(index='subject',columns='method',values='accuracy').dropna();delta=(a.nearest3-a.group_median).to_numpy();rng=np.random.default_rng(20261001);boot=[np.mean(rng.choice(delta,len(delta))) for _ in range(2000)]
r={'task':'noncausal PRE-to-DURING stage-transition development diagnostic','subjects':len(rows),'species_features':len(cols),'groups':d.groupby('Group').PatientID.nunique().to_dict(),'methods':{},'paired_subjects':len(delta),'nearest3_minus_group_median_accuracy':float(delta.mean()),'paired_subject_bootstrap_ci95':np.quantile(boot,[.025,.975]).tolist(),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'external_win_certified':False,'antibiotic_effect_claim':False}
for name,z in s.groupby('method'):r['methods'][name]={'subject_macro_accuracy':float(z.accuracy.mean()),'subject_macro_coverage':float(z.coverage.mean()),'subjects_no_scored_taxa':int(z.accuracy.isna().sum()),'total_eligible_taxon_changes':int(z.eligible.sum()),'total_scored_taxon_changes':int(z.scored.sum())}
r['common_scored_taxa_sensitivity']={'subjects':len(common),'nearest3_minus_group_median_accuracy':float(np.mean(common)),'ci95':np.quantile([np.mean(rng.choice(common,len(common))) for _ in range(2000)],[.025,.975]).tolist()}
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
