import json
from pathlib import Path
import pytest
from scripts.gut_material_identity import summarize_material


def sample(i, material='ENVO:feces'):
    return {'id':f'sample-{i}', 'attributes':{'sample-metadata':[
        {'key':'environment (material)','value':material},
        {'key':'environment (feature)','value':'ENVO:human-associated habitat'},
        {'key':'environment (biome)','value':'ENVO:human-associated habitat'},
        {'key':'host scientific name','value':'Homo sapiens'}]}}


def test_source_material_aggregate_and_cardinality():
    rows=[sample(1),sample(2)]
    assert summarize_material(rows,expected=2)['environment (material)']=={'ENVO:feces':2}
    with pytest.raises(ValueError,match='cardinality'):
        summarize_material([rows[0],rows[0]],expected=2)


def test_missing_or_conflicting_annotations_never_count_as_single_feces():
    rows=[sample(1),sample(2,'ENVO:skin')]
    assert summarize_material(rows,expected=2)['environment (material)']=={'ENVO:feces':1,'ENVO:skin':1}
    rows[1]['attributes']['sample-metadata'].append({'key':'environment (material)','value':'ENVO:feces'})
    assert summarize_material(rows,expected=2)['environment (material)']=={'ENVO:feces':1,'missing_or_ambiguous':1}


def test_observed_snapshot_preserves_uncertainty():
    d=json.loads(Path('results/gut_material_identity.json').read_text())
    assert d['all_source_samples']==529 and d['exact_mapped_retained_run_columns']==400
    assert d['all_source_sample_metadata']['environment (material)']=={'ENVO:feces':529}
    assert d['site_metadata_compatible'] is True
    assert 'canonical_linked_sample_fingerprint_sha256' not in d
    assert d['linked_retained_sample_metadata']['environment (material)']=={'ENVO:feces':400}
    # No source-family, actual specimen or external leaderboard claim follows from this snapshot.
    assert 'no independent specimen verification' in d['scope']
