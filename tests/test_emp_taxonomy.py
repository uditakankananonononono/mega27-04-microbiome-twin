from microtwin.emp_taxonomy import unambiguous_genus_mapping


def test_conflicting_parent_paths_are_excluded():
    labels, ambiguous = unambiguous_genus_mapping([
        [b'k__Bacteria', b'p__A', b'c__C', b'o__O', b'f__F1', b'g__Clostridium'],
        [b'k__Bacteria', b'p__A', b'c__C', b'o__O', b'f__F2', b'g__Clostridium'],
        [b'k__Bacteria', b'p__A', b'c__C', b'o__O', b'f__F3', b'g__Other'],
        [b'k__Bacteria', b'p__A', b'c__C', b'o__O', b'f__F3', b'g__Other'],
        [b'k__Bacteria', b'p__A', b'c__C', b'o__O', b'f__F3', b'g__'],
    ])
    assert ambiguous == {'Clostridium'}
    assert labels == [None, None, 'Other', 'Other', None]
