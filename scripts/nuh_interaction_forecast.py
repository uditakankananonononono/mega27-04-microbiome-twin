"""Subject-held-out exposed-development evaluation of the shipped interaction score."""
import sys,json,time,hashlib
from pathlib import Path
import numpy as np,pandas as pd
from microtwin.audit import fit_interaction,predict_interaction,fit_prior,predict_prior,bray_curtis

def main(path,out):
 start=time.monotonic();d=pd.read_csv(path,sep='\t');cols=[c for c in d if '|s__' in c and '|t__' not in c];X=d[cols].to_numpy(float)
 assert len(cols)==255 and np.isfinite(X).all() and (X>=0).all() and (X.sum(1)>0).all();X=X/X.sum(1,keepdims=True);rows=[]
 for subject,ix in d.groupby('PatientID').groups.items():
  s=d.loc[ix];a=s[s.TimePoint=='PRE'];b=s[s.TimePoint=='DURING'];assert len(a)==len(b)==1 and s.Group.nunique()==1
  rows.append((str(subject),s.Group.iloc[0],X[a.index[0]],X[b.index[0]]))
 rows.sort(key=lambda r:r[0]);assert len(rows)==24;pre=np.array([r[2] for r in rows]);post=np.array([r[3] for r in rows]);results=[]
 for held,r in enumerate(rows):
  tr=[i for i in range(24) if i!=held];assert held not in tr;P=post[tr];Z=(pre[held:held+1]>0)
  model=fit_interaction(P,100);preds={'interaction':predict_interaction(model,Z)[0],'matched_prior':predict_prior(fit_prior(P),Z)[0],'persistence':pre[held].copy()}
  # Explicit index exclusion makes the training arrays invariant to held-out outcome replacement.
  altered=post.copy();altered[held]=12345;assert np.array_equal(P,altered[tr])
  donors=[i for i in tr if rows[i][1]==r[1]];dist=bray_curtis(pre[donors],pre[held]);near=sorted(range(len(donors)),key=lambda j:(dist[j],rows[donors[j]][0]))[:3]
  for name,inds in [('group_median',donors),('nearest3',[donors[j] for j in near])]:
   q=np.maximum(0,pre[held]+np.median(post[inds]-pre[inds],axis=0));assert q.sum()>0;preds[name]=q/q.sum()
  truth=post[held]-pre[held];eligible=np.abs(truth)>=.001;assert eligible.any();met={}
  for name,q in preds.items():
   assert np.isfinite(q).all() and (q>=0).all() and np.isclose(q.sum(),1)
   delta=q-pre[held];nonzero=abs(delta)>1e-12;correct=(np.sign(delta)==np.sign(truth))&nonzero
   met[name]={'bc':float(bray_curtis(q,post[held])),'direction_accuracy_zero_wrong':float(correct[eligible].mean()),'direction_coverage':float(nonzero[eligible].mean())}
  met['decline_only']={'direction_accuracy_zero_wrong':float((truth[eligible]<0).mean()),'direction_coverage':1.0}
  results.append({'subject_label':'heldout_%02d'%(held+1),'eligible_taxa':int(eligible.sum()),'metrics':met})
 rng=np.random.default_rng(20261001);macro={name:{key:float(np.mean([r['metrics'][name][key] for r in results])) for key in results[0]['metrics'][name]} for name in met};comparisons={}
 for name in ['matched_prior','persistence','group_median','nearest3']:
  delta=np.array([r['metrics']['interaction']['bc']-r['metrics'][name]['bc'] for r in results]);boot=np.mean(delta[rng.integers(0,24,size=(2000,24))],axis=1)
  comparisons[name]={'interaction_minus_reference_mean_bc':float(delta.mean()),'subject_bootstrap_ci95':np.quantile(boot,[.025,.975]).tolist(),'interaction_lower_error_subjects':int((delta<0).sum())}
 report={'status':'exposed_development_noncausal_stage_forecast','subjects':24,'species':255,'lambda':100,'runtime_seconds':time.monotonic()-start,'source_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),'macro':macro,'bc_comparisons':comparisons,'held_out_training_array_invariance':'PASS','causal_or_external_validation_claim':False,'per_subject':results}
 Path(out).write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='per_subject'},indent=2))
if __name__=='__main__':main(*sys.argv[1:])
