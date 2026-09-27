"""Conservative metadata-only status matrix; UNKNOWN is not a pass."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
UNKNOWN='unknown'

def run(partial=None):
    d=json.loads(Path(partial or ROOT/'results/gut_analysis_metadata_crosswalk_partial.json').read_text())
    out=[]
    for r in d['completed_rows']:
        n=r['sample_count'];seen=r['sample_metadata_host_scientific_name_counts']
        names=sum(seen.values());missing=r.get('samples_without_usable_host_name')
        if missing is None:
            missing=max(0,n-names)
        if names+missing<n or names>n or missing>n:
            raise ValueError('host-name aggregate inconsistent')
        conflict=r['human_normalized_vs_nonhuman_host_name_conflict_samples']
        normalized=r['normalized_sample_species_counts']
        if conflict:
            host=False
        elif missing or normalized!={'Homo sapiens':n} or any(k.lower() not in ('homo sapiens','human') for k in seen):
            host=UNKNOWN
        else:host=True
        types=r['experiment_type_analysis_counts'];analysis_complete=sum(p['items'] for p in r['analysis_pages'])==r['analysis_count']
        sample_complete=sum(p['items'] for p in r['sample_pages'])==n
        out.append({'study':r['study'],'analysis_pagination_complete':analysis_complete,
                    'uniform_analysis_experiment_type':next(iter(types)) if len(types)==1 else UNKNOWN,
                    'sample_pagination_complete':sample_complete,'explicit_human_host_compatible':host,
                    'old_column_to_analysis_mapped':UNKNOWN,'independent_biological_family':UNKNOWN,
                    'missing_host_name_samples':missing})
    out.append({'study':d['unresolved_study'],'analysis_pagination_complete':UNKNOWN,
                'uniform_analysis_experiment_type':UNKNOWN,'sample_pagination_complete':UNKNOWN,
                'explicit_human_host_compatible':UNKNOWN,'old_column_to_analysis_mapped':UNKNOWN,
                'independent_biological_family':UNKNOWN,'missing_host_name_samples':UNKNOWN})
    # Narrow later finding: exact old SSU run-ID columns map to current analyses
    # and onward to samples for one already-viewed source. This does not resolve host.
    crosswalk=ROOT/'results/conflicted_host_column_identity.json'
    if partial is None and crosswalk.exists():
        c=json.loads(crosswalk.read_text())
        if not (c['retained_columns']==c['exact_run_matches_retained']==c['linked_retained_samples']
                ==c['unique_linked_retained_samples']==83):raise ValueError('exact run crosswalk incomplete')
        row=next(r for r in out if r['study']==c['study'])
        if row['explicit_human_host_compatible'] is not False:raise ValueError('host conflict was lost')
        row['old_column_to_analysis_mapped']=True
    oral=ROOT/'results/oral_column_identity.json'
    if partial is None and oral.exists():
        c=json.loads(oral.read_text())
        if not (c['retained_columns']==c['exact_retained_run_matches']
                ==c['retained_selected_pipeline_5_0_analysis_records']
                ==c['linked_sample_relationships']==c['unique_linked_sample_ids']==111):
            raise ValueError('oral run crosswalk incomplete')
        row=next(r for r in out if r['study']==c['study'])
        if row['explicit_human_host_compatible'] is not True:raise ValueError('oral host compatibility changed')
        row['old_column_to_analysis_mapped']=True
    return {'rows':sorted(out,key=lambda x:x['study']),'n_studies':len(out),
            'scope':'metadata-only partial screen plus exact current run-column mapping for MGYS00006755 and MGYS00002238; no final source eligibility or independent validation',
            'unknown_is_not_pass':True}
if __name__=='__main__':
    d=run();(ROOT/'results/metadata_integrity_matrix.json').write_text(json.dumps(d,indent=2)+'\n')
    for r in d['rows']:print(r)
