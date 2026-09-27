"""Exploratory MGnify project-ID sensitivity; predeclared in results/PREREG_20260927_source_family_sensitivity.md."""
import json
import re
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def run():
    manifest=pd.read_csv(ROOT/'data/raw/mgnify/manifest.csv')
    audit=pd.read_csv(ROOT/'results/mgnify_audit_fdr.csv')
    assert manifest.study.is_unique and audit.study.is_unique
    assert set(manifest.study)==set(audit.study) and len(audit)==160
    a=audit.merge(manifest[['study','study_name','secondary_accession']],on='study',validate='one_to_one')
    family=[]; resolution=[]
    for row in a.itertuples():
        tokens=set(re.findall(r'PRJ(?:NA|EB|DB)\d+',str(row.study_name).upper()))
        if len(tokens)==1:
            family.append(next(iter(tokens))); resolution.append('one_token')
        else:
            family.append('unresolved:'+row.study); resolution.append('none' if not tokens else 'ambiguous')
    a['family']=family;a['resolution']=resolution
    a['relative_gain']=a.gain/a.median_prior
    size=a.groupby('family').size(); repeated=size[size>1]
    sorted_a=a.sort_values('study'); chosen=sorted_a.drop_duplicates('family',keep='first')
    overall=lambda x:{'rows':int(len(x)),'original_fdr_interaction_wins':int(x.int_wins.sum()),'original_fdr_prior_wins':int(x.prior_wins.sum()),'median_relative_gain':float(x.relative_gain.median()),'median_absolute_gain':float(x.gain.median())}
    repeats=[]
    for f,n in repeated.items():
        rows=a[a.family==f].sort_values('study')
        repeats.append({'family':f,'tables':rows.study.tolist(),'n':int(n),'original_fdr_interaction_wins':int(rows.int_wins.sum()),'prior_wins':int(rows.prior_wins.sum()),'relative_gains':[float(z) for z in rows.relative_gain], 'win_status_discordant':len(set(rows.int_wins))>1})
    out={'method':'original-project token from study_name; lexical MGYS one-per-family; same 160-table BH q values',
         'unresolved_rows':int((a.resolution!='one_token').sum()),'single_token_rows':int((a.resolution=='one_token').sum()),
         'provisional_families':int(a.family.nunique()),'repeated_families':len(repeated),'rows_in_repeated_families':int(repeated.sum()),
         'original':overall(a),'lexical_one_per_family':overall(chosen),
         'family_median_of_member_mean_relative_gain':float(a.groupby('family').relative_gain.mean().median()),
         'repeated_family_details':repeats,'caveat':'Provisional original project IDs are not verified biological units; unresolved groups are treated as distinct, not certified independent. Viewed exploratory sensitivity.'}
    return out
if __name__=='__main__':
    out=run();(ROOT/'results/mgnify_family_sensitivity.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='repeated_family_details'},indent=2))
