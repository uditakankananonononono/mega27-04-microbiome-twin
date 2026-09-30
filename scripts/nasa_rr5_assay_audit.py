"""Small-table exploratory RR-5 matched fecal genus audit; no raw reads."""
import sys,json,re,hashlib
from pathlib import Path
import pandas as pd
import numpy as np
from scipy.stats import wilcoxon,spearmanr
from scipy.spatial.distance import braycurtis
from statsmodels.stats.multitest import multipletests
root=Path(sys.argv[1]); out=Path(sys.argv[2]);out.mkdir(exist_ok=True,parents=True)
s=pd.read_csv(root/'isa/s_OSD-417.txt',sep='\t')
a=pd.read_csv(next((root/'isa').glob('*hiseq2500*')),sep='\t')
w=pd.read_csv(next((root/'isa').glob('*novaseq*')),sep='\t')
x=pd.read_csv(root/'GLDS-417_GAmplicon_V4-taxonomy-and-counts.tsv',sep='\t').fillna({'genus':'UNASSIGNED'})
y=pd.read_csv(root/'GLDS-417_GMetagenomics_Metaphlan-taxonomy_GLmetagenomics.tsv',sep='\t',skiprows=1)
xg=x.groupby('genus')[list(x.columns[8:])].sum();xg=xg/xg.sum()
yi=y.clade_name.str.contains(r'\|g__') & ~y.clade_name.str.contains(r'\|s__')
yg=y[yi].copy();yg['genus']=yg.clade_name.str.split('g__').str[-1];yg=yg.drop(columns='clade_name').groupby('genus').sum()/100
pairs=[]
for _,row in w.iterrows():
 name=row['Sample Name'].removesuffix('_WGS'); ar=a[a['Sample Name']==name]
 assert len(ar)==1
 xc=re.search(r'GLDS-417_Amplicon_(.*?)_R1_raw',ar.iloc[0]['Raw Data File']).group(1)
 yc=re.search(r'GLDS-417_metagenomics_(.*?)_R1_HRremoved',row['Raw Data File']).group(1)
 meta=s[s['Sample Name']==row['Sample Name']];assert len(meta)==1
 m=meta.iloc[0]
 pairs.append(dict(v4=xc,shotgun=yc,mouse=m['Source Name'],rfid=m['Comment[RFID(last 4 digit)]'],material=m['Characteristics[Material Type]'],time=m['Factor Value[Time]'],group=m['Factor Value[Spaceflight]'],cage=int(m['Parameter Value[Mouse Cage ID]'])))
pd.DataFrame(pairs).to_csv(out/'paired_mouse_mapping.csv',index=False)
assert len({p['rfid'] for p in pairs})==20
X=xg[[p['v4'] for p in pairs]].copy();Y=yg[[p['shotgun'] for p in pairs]].copy();X.columns=Y.columns=range(20)
# Keep total-sample denominator; unmatched mass explicit; do not renormalize intersection.
shared=sorted(set(X.index)&set(Y.index));eligible=[g for g in shared if ((X.loc[g]>0)|(Y.loc[g]>0)).mean()>=.2]
rows=[]
for g in eligible:
 xv=X.loc[g].to_numpy();yv=Y.loc[g].to_numpy();delta=yv-xv
 p=wilcoxon(delta).pvalue if np.any(delta) else 1
 rows.append(dict(genus=g,v4_median_pct=float(np.median(xv)*100),shotgun_median_pct=float(np.median(yv)*100),median_paired_difference_pp=float(np.median(delta)*100),p=float(p),spearman=float(spearmanr(xv,yv).statistic)))
q=multipletests([r['p'] for r in rows],method='fdr_bh')[1]
for r,v in zip(rows,q):r['q']=float(v)
t=pd.DataFrame(rows).sort_values('q');t.to_csv(out/'paired_genus_results.csv',index=False)
union=sorted(set(X.index)|set(Y.index));xx=X.reindex(union,fill_value=0); yy=Y.reindex(union,fill_value=0)
# Separate residual bins, as taxonomically unassigned mass is not demonstrably same clade.
yun=y.set_index('clade_name').loc['UNCLASSIFIED',[p['shotgun'] for p in pairs]].to_numpy(dtype=float)/100
xx.loc['SHOTGUN_UNCLASSIFIED']=0;yy.loc['SHOTGUN_UNCLASSIFIED']=yun
bc=[braycurtis(xx[i],yy[i]) for i in range(20)]
res=dict(n_matched_mice=20,cages=sorted({p['cage'] for p in pairs}),groups=pd.DataFrame(pairs).groupby('group').size().to_dict(),shared_genera=len(shared),tested_genera=len(eligible),q_lt_005=int((t.q<.05).sum()),median_bray_curtis=float(np.median(bc)),v4_unassigned_median_pct=float(X.loc['UNASSIGNED'].median()*100),shotgun_unclassified_median_pct=float(np.median(yun)*100),result_type='exploratory measurement concordance, not independent biological replication',input_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.glob('*.tsv')})
(out/'summary.json').write_text(json.dumps(res,indent=2)); print(json.dumps(res,indent=2));print(t.head(12).to_string(index=False))
