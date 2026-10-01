"""Frozen baseline-conditioned PRE-to-DURING development forecast; no causal claim."""
import sys,json,time,hashlib
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.linear_model import Ridge
from microtwin.audit import bray_curtis

def main(path,out):
 start=time.monotonic();d=pd.read_csv(path,sep='\t');cols=[c for c in d if '|s__' in c and '|t__' not in c];X=d[cols].to_numpy(float);assert len(cols)==255 and np.isfinite(X).all() and (X>=0).all() and (X.sum(1)>0).all();X/=X.sum(1,keepdims=True);rows=[]
 for subject,ix in d.groupby('PatientID').groups.items():
  s=d.loc[ix];a=s[s.TimePoint=='PRE'];b=s[s.TimePoint=='DURING'];assert len(a)==len(b)==1 and s.Group.nunique()==1
  rows.append((str(subject),s.Group.iloc[0],X[a.index[0]],X[b.index[0]]))
 rows.sort(key=lambda r:r[0]);assert len(rows)==24;pre=np.array([r[2] for r in rows]);post=np.array([r[3] for r in rows]);raw=np.column_stack([np.log1p(1000*pre),[float(r[1]=='Case') for r in rows]]);results=[]
 for held,r in enumerate(rows):
  tr=[i for i in range(24) if i!=held];mu=raw[tr].mean(0);sd=raw[tr].std(0);sd[sd==0]=1;features=(raw-mu)/sd;target=(post-pre)[tr];altered=post.copy();altered[held]=12345
  assert held not in tr and np.array_equal(target,(altered-pre)[tr]);assert np.array_equal(mu,raw[tr].mean(0))
  model=Ridge(alpha=10,fit_intercept=True,solver='svd').fit(features[tr],target)
  q=np.maximum(0,pre[held]+model.predict(features[held:held+1])[0]);assert q.sum()>0
  preds={'transition_ridge':q/q.sum(),'persistence':pre[held].copy()};donors=[i for i in tr if rows[i][1]==r[1]];dist=bray_curtis(pre[donors],pre[held]);near=sorted(range(len(donors)),key=lambda j:(dist[j],rows[donors[j]][0]))[:3]
  for name,inds in [('group_median',donors),('nearest3',[donors[j] for j in near])]:
   q=np.maximum(0,pre[held]+np.median(post[inds]-pre[inds],axis=0));assert q.sum()>0;preds[name]=q/q.sum()
  truth=post[held]-pre[held];eligible=abs(truth)>=.001;assert eligible.any();metrics={}
  for name,q in preds.items():
   assert np.isfinite(q).all() and (q>=0).all() and np.isclose(q.sum(),1)
   delta=q-pre[held];attempted=abs(delta)>1e-12;correct=(np.sign(delta)==np.sign(truth))&attempted
   metrics[name]={'bc':float(bray_curtis(q,post[held])),'direction_accuracy_zero_wrong':float(correct[eligible].mean()),'coverage':float(attempted[eligible].mean())}
  metrics['decline_only']={'direction_accuracy_zero_wrong':float((truth[eligible]<0).mean()),'coverage':1.0}
  results.append({'heldout_index':held+1,'submitted_group':r[1],'eligible':int(eligible.sum()),'metrics':metrics})
 rng=np.random.default_rng(20261001);macro={name:{key:float(np.mean([r['metrics'][name][key] for r in results])) for key in metrics[name]} for name in metrics};comparisons={}
 for name in ['persistence','group_median','nearest3']:
  delta=np.array([r['metrics']['transition_ridge']['bc']-r['metrics'][name]['bc'] for r in results]);draws=np.mean(delta[rng.integers(0,24,size=(2000,24))],axis=1);ci=np.quantile(draws,[.025,.975]).tolist()
  comparisons[name]={'ridge_minus_reference_mean_bc':float(delta.mean()),'ci95':ci,'lower_error_subjects':int((delta<0).sum()),'bc_useful_win':bool(delta.mean()<=-.02 and ci[1]<0)}
 direction_pass=macro['transition_ridge']['direction_accuracy_zero_wrong']>=max(macro[n]['direction_accuracy_zero_wrong'] for n in ['group_median','decline_only']);group_summaries={}
 for g in sorted(set(r['submitted_group'] for r in results)):
  subset=[r for r in results if r['submitted_group']==g];group_summaries[g]={n:float(np.mean([r['metrics'][n]['bc'] for r in subset])) for n in ['transition_ridge','persistence','group_median','nearest3']}
 report={'status':'exposed_noncausal_development','fits':24,'features':256,'species':255,'alpha':10,'runtime_seconds':time.monotonic()-start,'source_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),'macro':macro,'comparisons':comparisons,'group_mean_bc':group_summaries,'direction_criterion_met':bool(direction_pass),'useful_win':bool(direction_pass and all(c['bc_useful_win'] for c in comparisons.values())),'held_out_exclusion_invariance':'PASS','stage_identifiability':'single transition type, stage conditioning is task selection only','causal_or_external_win':False,'per_subject':results}
 Path(out).write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='per_subject'},indent=2))
if __name__=='__main__':main(*sys.argv[1:])
