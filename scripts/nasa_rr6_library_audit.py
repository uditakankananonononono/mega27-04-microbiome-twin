import sys,json,re
from pathlib import Path
import pandas as pd,numpy as np
from scipy.spatial.distance import braycurtis
r=Path(sys.argv[1]);o=Path(sys.argv[2]);o.mkdir(exist_ok=True,parents=True)
s=pd.read_csv(r/'isa/s_OSD-249.txt',sep='\t')
g={};u={};mapping=[]
for kit in ['NxtaFlex','Swift1S']:
 t=pd.read_csv(r/f'GLDS-249_GMetagenomics_{kit}_Metaphlan-taxonomy.tsv',sep='\t',skiprows=1)
 names=list(t.columns[2:]);mapped=[n.replace('_'+kit+'_','_') for n in names];assert len(set(mapped))==48
 # Verify table columns against original filenames and shared extract IDs.
 a=None
 for p in (r/'isa').glob('a_*NovaSeq*'):
  z=pd.read_csv(p,sep='\t')
  if z['Raw Data File'].str.contains('_'+kit+'_').all():a=z;break
 assert a is not None
 for col,name in zip(names,mapped):
  row=a[a['Sample Name']==name];assert len(row)==1 and col in row.iloc[0]['Raw Data File'];meta=s[s['Sample Name']==name];assert len(meta)==1
  mapping.append(dict(kit=kit,sample=name,column=col,extract=row.iloc[0]['Extract Name'],source=meta.iloc[0]['Source Name'],subject=meta.iloc[0]['Comment[ALSDA Biospecimen Subject ID]']))
 idx=t.clade_name.str.contains(r'\|g__') & ~t.clade_name.str.contains(r'\|s__');z=t[idx].copy();z['genus']=z.clade_name.str.split('g__').str[-1];z=z.drop(columns=['clade_name','NCBI_tax_id']).groupby('genus').sum()/100;z.columns=mapped;g[kit]=z
 un=t.set_index('clade_name').loc['UNKNOWN',names]/100;un.index=mapped;u[kit]=un
md=pd.DataFrame(mapping);assert md.groupby('sample').extract.nunique().eq(1).all();assert md.groupby('sample').subject.nunique(dropna=False).eq(1).all();md.to_csv(o/'library_mapping.csv',index=False)
names=sorted(g['NxtaFlex'].columns);un1=u['NxtaFlex'][names];un2=u['Swift1S'][names]
rows=[]
for name in names:
 a=g['NxtaFlex'][name];b=g['Swift1S'][name];idx=sorted(set(a.index)|set(b.index));aa=a.reindex(idx,fill_value=0);bb=b.reindex(idx,fill_value=0)
 rows.append(dict(sample=name,nxtaflex_unknown_pct=un1[name]*100,swift_unknown_pct=un2[name]*100,delta_unknown_pp=(un2[name]-un1[name])*100,assigned_composition_bray_curtis=braycurtis(aa/aa.sum(),bb/bb.sum())))
pd.DataFrame(rows).to_csv(o/'per_sample_results.csv',index=False)
amp=pd.read_csv(r/'GLDS-249_GAmplicon_FluidAA_taxonomy-and-counts.tsv',sep='\t').fillna({'genus':'UNASSIGNED'});ag=amp.groupby('genus')[list(amp.columns[8:])].sum();ag=ag/ag.sum();ag.columns=[n.replace('_FluidAA_','_') for n in ag.columns];assert set(ag.columns)==set(names)
a=pd.read_csv(next((r/'isa').glob('*MiniSeq*')),sep='\t');assert set(a['Sample Name'])==set(names)
summ={}
for kit in g:
 av=ag.loc['Blautia',names];bv=g[kit].loc['Blautia',names]
 summ[kit]={'amplicon_median_pct':float(av.median()*100),'shotgun_median_pct':float(bv.median()*100),'amplicon_higher_pairs':int((av>bv).sum()),'assigned_only_amplicon_median_pct':float((av/(1-ag.loc['UNASSIGNED',names])).median()*100),'assigned_only_shotgun_median_pct':float((bv/g[kit][names].sum()).median()*100),'assigned_only_amplicon_higher_pairs':int(((av/(1-ag.loc['UNASSIGNED',names]))>(bv/g[kit][names].sum())).sum())}
z=pd.DataFrame(rows);res={'n_matched_samples':48,'biospecimen_subject_id_values_not_individual_count':int(md.subject.nunique()),'sample_identity_caveat':'48 distinct sample/source labels; alternate ALSDA source IDs contain duplicate 3E6E and Biospecimen Subject ID is cohort-level','same_extract_per_sample':True,'nxtaflex_unknown_median_pct':float(un1.median()*100),'swift_unknown_median_pct':float(un2.median()*100),'swift_lower_unknown_pairs':int((un2<un1).sum()),'median_paired_unknown_difference_pp':float(((un2-un1)*100).median()),'assigned_bray_curtis_median':float(z.assigned_composition_bray_curtis.median()),'Blautia':summ,'status':'exploratory library-preparation sensitivity, not biological flight effect'}
(o/'summary.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
