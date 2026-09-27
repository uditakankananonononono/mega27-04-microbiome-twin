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
    return {'rows':sorted(out,key=lambda x:x['study']),'n_studies':len(out),
            'scope':'metadata-only partial screen; no final source eligibility or assay-certified result',
            'unknown_is_not_pass':True}
if __name__=='__main__':
    d=run();(ROOT/'results/metadata_integrity_matrix.json').write_text(json.dumps(d,indent=2)+'\n')
    for r in d['rows']:print(r)
