"""Frozen global residual community/transcriptome RV permutation test."""
import json,sys,time,hashlib
from pathlib import Path
import pandas as pd,numpy as np
from statsmodels.stats.multitest import multipletests
start=time.monotonic();host=Path(sys.argv[1]);micro=Path(sys.argv[2]);out=Path(sys.argv[3]);out.mkdir(parents=True,exist_ok=True)
Gs={}
for kit in ['Swift1S','NxtaFlex']:
 d=pd.read_csv(micro/f'GLDS-249_GMetagenomics_{kit}_Metaphlan-taxonomy.tsv',sep='\t',skiprows=1);d=d[d.clade_name.str.contains(r'\|g__')&~d.clade_name.str.contains(r'\|s__')].copy();d['genus']=d.clade_name.str.split('g__').str[-1];d=d.drop(columns=['clade_name','NCBI_tax_id']).groupby('genus').sum();d.columns=[c.replace('_'+kit+'_','_') for c in d.columns];Gs[kit]=d
amp=pd.read_csv(micro/'GLDS-249_GAmplicon_FluidAA_taxonomy-and-counts.tsv',sep='\t').fillna({'genus':'UNASSIGNED'});ag=amp.groupby('genus')[list(amp.columns[8:])].sum().drop(index='UNASSIGNED');ag.columns=[c.replace('_FluidAA_','_') for c in ag.columns];Gs['16S']=ag
results=[]
for acc in ['OSD-247','OSD-245']:
 md=pd.read_csv(Path('results/nasa_rr6_host_20260930')/(acc+'-accepted-mapping.csv'));n=len(md);strata=md.stratum.to_numpy();groups=[np.where(strata==s)[0] for s in np.unique(strata)]
 f=host/f'GLDS-{acc[4:]}_rna_seq_Normalized_Counts_rRNArm_GLbulkRNAseq.csv';h=pd.read_csv(f,index_col=0)[list(md.Sample_Name_host)] if 'Sample_Name_host' in md else pd.read_csv(f,index_col=0)[list(md['Sample Name_host'])]
 keep=(h.mean(axis=1)>=10)&((h>0).mean(axis=1)>=.8);h=h[keep];H=np.log1p(h.to_numpy(float).T);std=H.std(axis=0);valid=std>0;h=h.iloc[np.where(valid)[0]];H=H[:,valid];H=(H-H.mean(axis=0))/std[valid]
 for ix in groups:H[ix]-=H[ix].mean(axis=0)
 B=H@H.T;bnorm=np.sqrt((B*B).sum());pd.Series(h.index,name='gene_id').to_csv(out/(acc+'-tested-genes.csv'),index=False)
 for kit,g in Gs.items():
  X=g[list(md['Sample Name_micro'])].to_numpy(float).T;X=np.sqrt(X/X.sum(axis=1,keepdims=True))
  for ix in groups:X[ix]-=X[ix].mean(axis=0)
  A=X@X.T;den=np.sqrt((A*A).sum())*bnorm;stat=float((A*B).sum()/den);rng=np.random.default_rng(20260930);ge=0;permstats=[]
  for k in range(9999):
   if time.monotonic()-start>115:raise RuntimeError('bounded runtime exhausted')
   p=np.arange(n)
   for ix in groups:p[ix]=rng.permutation(ix)
   v=float((A*B[np.ix_(p,p)]).sum()/den);ge+=v>=stat;permstats.append(v)
  results.append(dict(tissue=acc,kit=kit,n=n,strata=len(groups),host_genes=len(h),microbe_genera=len(g),RV=stat,within_stratum_permutation_p=(ge+1)/10000,permutations=9999,seed=20260930,null_median=float(np.median(permstats)),host_source_sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
res=pd.DataFrame(results);primary=res.kit=='Swift1S';res.loc[primary,'primary_BH_q']=multipletests(res.loc[primary,'within_stratum_permutation_p'],method='fdr_bh')[1];res.to_csv(out/'global_tests.csv',index=False);print(res.drop(columns='host_source_sha256').to_string(index=False));print('runtime_seconds',time.monotonic()-start)
