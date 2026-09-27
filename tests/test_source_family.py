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


def test_duplicate_alias_in_same_family_is_not_silently_accepted():
    with pytest.raises(ValueError, match='duplicate accession'):
        check_family_partitions([], {'same': ['PRJEB71357', 'prjeb71357']})
    with pytest.raises(ValueError, match='requires aliases'):
        check_family_partitions([], {'empty': []})
    with pytest.raises(ValueError, match='mapping'):
        check_family_partitions([], {'none': None})


def test_mgnify_prjna715245_aliases_cannot_cross_partitions():
    from microtwin.source_family import known_mgnify_original_project_families
    aliases = known_mgnify_original_project_families()
    assert len(aliases['PRJNA715245']) == 7
    result = check_family_partitions([
        {'accession': 'MGYS00006825', 'partition': 'train'},
        {'accession': 'ERP175206', 'partition': 'test'}], aliases)
    assert not result['valid_known_family_separation_only']
    assert {'reason': 'cross_partition_family', 'family': 'PRJNA715245',
            'partitions': ['test', 'train']} in result['errors']
    assert check_family_partitions([
        {'accession': 'PRJEB75554', 'partition': 'test'},
        {'accession': 'MGYS00006862', 'partition': 'test'}], aliases)['valid_known_family_separation_only']
    assert not check_family_partitions([
        {'accession': 'UNKNOWN', 'partition': 'test'}], aliases)['valid_known_family_separation_only']
