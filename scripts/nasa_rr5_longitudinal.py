import sys,re,json
from pathlib import Path
import pandas as pd,numpy as np
from scipy.spatial.distance import braycurtis
root=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
s=pd.read_csv(root/'isa/s_OSD-417.txt',sep='\t'); rows=[]
for assay,platform,tag in [('fecal','hiseq2500','V4'),('oral','miseq','V1V3')]:
 a=pd.read_csv(next((root/'isa').glob('*'+platform+'*')),sep='\t')
 t=pd.read_csv(root/f'GLDS-417_GAmplicon_{tag}-taxonomy-and-counts.tsv',sep='\t').fillna({'genus':'UNASSIGNED'})
 g=t.groupby('genus')[list(t.columns[8:])].sum();g=g/g.sum()
 mapping=[]
 for _,z in a.iterrows():
  meta=s[s['Sample Name']==z['Sample Name']];assert len(meta)==1;m=meta.iloc[0]
  if int(m['Parameter Value[Mouse Cage ID]']) not in [215,216]:continue
  raw=z['Raw Data File'];col=re.search(r'GLDS-417_Amplicon_(.*?)_R1_raw',raw).group(1)
  if assay=='fecal' and col.endswith('final'):continue # necropsy distinct from fresh-fecal week 9
  mapping.append(dict(col=col,rfid=m['Comment[RFID(last 4 digit)]'],group=m['Factor Value[Spaceflight]'],cage=int(m['Parameter Value[Mouse Cage ID]']),time=m['Factor Value[Time]'],sample=z['Sample Name']))
 md=pd.DataFrame(mapping)
 assert md.groupby('rfid').size().eq(3).all() and md.rfid.nunique()==20
 for mouse,d in md.groupby('rfid'):
  by={float(z.time.split()[-1]):z for z in d.itertuples()};assert set(by)=={0,4.5,9}
  base=g[by[0].col];d45=braycurtis(base,g[by[4.5].col]);d9=braycurtis(base,g[by[9].col])
  rows.append(dict(assay=assay,rfid=mouse,group=by[0].group,cage=by[0].cage,distance_45=d45,distance_9=d9,recovery_difference=d9-d45))
 md.to_csv(out/f'{assay}_sample_mapping.csv',index=False)
r=pd.DataFrame(rows);r.to_csv(out/'per_mouse_distances.csv',index=False);summary=[]
for (assay,group),d in r.groupby(['assay','group']):
 summary.append(dict(assay=assay,group=group,n_mice=len(d),cages=d.cage.unique().tolist(),median_distance_45=d.distance_45.median(),median_distance_9=d.distance_9.median(),median_recovery_difference=d.recovery_difference.median(),closer_to_baseline_at_9=int((d.recovery_difference<0).sum())))
(out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
