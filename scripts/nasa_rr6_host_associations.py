"""Four frozen exploratory same-subject tests; no predictive model."""
import sys,json
from pathlib import Path
import pandas as pd,numpy as np
from scipy.stats import rankdata,spearmanr,t as student_t
from statsmodels.stats.multitest import multipletests
host=Path(sys.argv[1]);micro=Path(sys.argv[2]);out=Path(sys.argv[3]);out.mkdir(parents=True,exist_ok=True)
m=pd.read_csv(micro/'isa/s_OSD-249.txt',sep='\t'); ids=json.load(open(host/'gene_ids.json'))
geneids={}
for gene,z in ids.items():
 hit=z['result']['hits'];assert len(hit)==1 and hit[0]['symbol']==gene
 en=hit[0]['ensembl'];en=[en] if isinstance(en,dict) else en
 choices=[x['gene'] for x in en if x['gene'].startswith('ENSMUSG')];assert len(choices)==1;geneids[gene]=choices[0]
g={}
for kit in ['Swift1S','NxtaFlex']:
 d=pd.read_csv(micro/f'GLDS-249_GMetagenomics_{kit}_Metaphlan-taxonomy.tsv',sep='\t',skiprows=1);d=d[d.clade_name.str.contains(r'\|g__')&~d.clade_name.str.contains(r'\|s__')].copy();d['genus']=d.clade_name.str.split('g__').str[-1];d=d.drop(columns=['clade_name','NCBI_tax_id']).groupby('genus').sum()/100;d.columns=[c.replace('_'+kit+'_','_') for c in d.columns];g[kit]=d
amp=pd.read_csv(micro/'GLDS-249_GAmplicon_FluidAA_taxonomy-and-counts.tsv',sep='\t').fillna({'genus':'UNASSIGNED'});ag=amp.groupby('genus')[list(amp.columns[8:])].sum();ag/=ag.sum();ag.columns=[c.replace('_FluidAA_','_') for c in ag.columns];g['16S']=ag
rows=[];vals=[]
for acc,tests in [('OSD-247',[('Muc2','Blautia'),('Ffar2','Intestinimonas')]),('OSD-245',[('Cyp7a1','Blautia'),('Nr1h4','Parabacteroides')])]:
 h=pd.read_csv(host/acc/('s_'+acc+'.txt'),sep='\t');col='Comment[LSDA Source Name]' if acc=='OSD-247' else 'Comment[ALSDA Source Name]'
 mm=m.copy();hh=h.copy();mm['individual_id']=mm['Comment[ALSDA Source Name]'].astype(str).str.strip();hh['individual_id']=hh[col].astype(str).str.strip()
 z=mm.merge(hh,on='Source Name',suffixes=('_micro','_host'));z=z[z.individual_id_micro==z.individual_id_host].copy();assert not z.individual_id_micro.duplicated().any()
 z['stratum']=z['Sample Name_micro'].str.extract(r'FCS_(.*?)_Rep')[0];z.to_csv(out/(acc+'-accepted-mapping.csv'),index=False)
 wanted=set(geneids[gene] for gene,_ in tests);chunks=[]
 for c in pd.read_csv(host/f'GLDS-{acc[4:]}_rna_seq_Normalized_Counts_rRNArm_GLbulkRNAseq.csv',index_col=0,chunksize=5000):chunks.append(c[c.index.isin(wanted)])
 expr=pd.concat(chunks);assert set(expr.index)==wanted;expr.to_csv(out/(acc+'-selected-expression.csv'))
 for gene,taxon in tests:
  y=expr.loc[geneids[gene],z['Sample Name_host']].to_numpy(float); stratum=z.stratum.to_numpy()
  for kit,gg in g.items():
   x=gg.loc[taxon,z['Sample Name_micro']].to_numpy(float);xr=np.zeros(len(x));yr=np.zeros(len(y))
   for st in np.unique(stratum):
    ix=stratum==st;xr[ix]=rankdata(x[ix])-rankdata(x[ix]).mean();yr[ix]=rankdata(y[ix])-rankdata(y[ix]).mean()
   rho=float(np.corrcoef(xr,yr)[0,1]);df=len(x)-len(np.unique(stratum))-1
   p=float(2*student_t.sf(abs(rho)*np.sqrt(df/max(1-rho*rho,1e-15)),df))
   rows.append(dict(tissue=acc,gene=gene,taxon=taxon,kit=kit,n=len(x),strata=len(np.unique(stratum)),within_stratum_rank_correlation=rho,approximate_independent_sample_p=p,pooled_spearman=float(spearmanr(x,y).statistic)))
   for i,src in enumerate(z['Source Name']):vals.append(dict(tissue=acc,gene=gene,taxon=taxon,kit=kit,source=src,stratum=stratum[i],microbe_abundance=x[i],host_expression=y[i]))
r=pd.DataFrame(rows);primary=r.kit=='Swift1S';r.loc[primary,'primary_BH_q']=multipletests(r.loc[primary,'approximate_independent_sample_p'],method='fdr_bh')[1]
r.to_csv(out/'four_tests.csv',index=False);pd.DataFrame(vals).to_csv(out/'individual_values.csv',index=False);print(r.to_string(index=False))
