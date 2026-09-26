import pytest
from microtwin.source_family import check_family_partitions

FAMILIES = {'anthony-2022': ['PRJNA664754', 'MGYS00006765', 'PRJEB75578'],
            'ceremi': ['PRJEB28341', 'PRJEB58157'],
            'other': ['PRJEB71357']}


def test_parent_assembly_alias_crosses_partition():
    result = check_family_partitions([{'accession': 'MGYS00006765', 'partition': 'train'},
                                      {'accession': 'PRJNA664754', 'partition': 'test'}], FAMILIES)
    assert not result['valid_known_family_separation_only']
    assert result['errors'][0]['reason'] == 'cross_partition_family'


def test_two_ceremi_modalities_cannot_be_independent():
    r = check_family_partitions([{'accession': 'PRJEB28341', 'partition': 'validation'},
                                 {'accession': 'PRJEB58157', 'partition': 'test'}], FAMILIES)
    assert not r['valid_known_family_separation_only']


def test_unknown_family_fails_closed_and_separate_known_only_passes_narrow_check():
    x = check_family_partitions([{'accession': 'PRJEB71357', 'partition': 'test'}], FAMILIES)
    assert x['valid_known_family_separation_only']
    assert 'does not establish rights' in x['note']
    y = check_family_partitions([{'accession': 'NEW', 'partition': 'test'}], FAMILIES)
    assert not y['valid_known_family_separation_only']
    with pytest.raises(ValueError, match='conflicting'):
        check_family_partitions([], {'one': ['PRJEB71357'], 'two': ['PRJEB71357']})
