from microtwin.split_guard import validate_disjoint


def _row(p, source, study, subject=None, fingerprint=None):
    return dict(partition=p, source=source, study=study,
                subject=subject, fingerprint=fingerprint)


def test_clean_source_holdout():
    r = validate_disjoint([_row("train", "A", "S1", "P1", "hash1"),
                           _row("test", "B", "S2", "P2", "hash2")])
    assert r["valid"]


def test_nested_leakage_is_rejected():
    r = validate_disjoint([_row("train", "A", "S1", "P1", "hash1"),
                           _row("test", "B", "S2", "P1", "hash1")])
    assert not r["valid"]
    assert {x["reason"] for x in r["errors"]} >= {"cross_partition_subject", "cross_partition_fingerprint"}


def test_same_study_in_different_partition_is_rejected():
    r = validate_disjoint([_row("train", "A", "S1"), _row("test", "A", "S1")])
    assert not r["valid"]
    assert {x["reason"] for x in r["errors"]} >= {"cross_partition_source", "cross_partition_study"}


def test_unknown_source_cannot_pass():
    assert not validate_disjoint([_row("train", "", "S1")])["valid"]
