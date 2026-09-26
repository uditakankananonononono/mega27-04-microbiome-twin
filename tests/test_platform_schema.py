import pytest
from microtwin.platform_schema import validate_abundance_table


def test_requires_processing_consent_and_valid_units():
    kwargs = dict(taxa=['A','B'], samples=['S1'], values=[[.2,.8]], unit='relative_abundance', source_id='study-1')
    with pytest.raises(ValueError, match='consent'):
        validate_abundance_table(**kwargs)
    out = validate_abundance_table(**kwargs, consent_for_processing=True)
    assert out['status'] == 'schema_validated_only'


def test_rejects_wrong_shape_zero_sample_and_bad_relative_abundance():
    args = dict(taxa=['A','B'], samples=['S1'], unit='relative_abundance', source_id='study-1', consent_for_processing=True)
    for values in ([[0,0]], [[.2,.2]], [[.2]], [[-.2,1.2]]):
        with pytest.raises(ValueError): validate_abundance_table(**args, values=values)
