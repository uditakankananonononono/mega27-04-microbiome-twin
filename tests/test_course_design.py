import pytest
from microtwin.course_design import screen_courses


def sample(s, t, source='A'):
    return {'source_family': source, 'subject': s, 'sample': f'{source}-{s}-{t}', 'time': t}


def course(s, a, b, source='A'):
    return {'source_family': source, 'subject': s, 'start': a, 'end': b, 'arm': 'exposed'}


def test_single_course_has_one_valid_prepost_window():
    r = screen_courses([sample('x', 0), sample('x', 10)], [course('x', 2, 5)])
    assert r['courses_with_pre_and_post_sample'] == 1
    assert r['subjects_with_at_least_one_unambiguous_window'] == 1
    assert r['status'] == 'metadata_only_no_outcomes'


def test_overlapping_course_blocks_even_with_prepost_samples():
    r = screen_courses([sample('x', 0), sample('x', 10)], [course('x', 2, 5), course('x', 4, 7)])
    assert r['courses_with_pre_and_post_sample'] == 2
    assert r['courses_blocked_by_other_exposure_in_window'] == 2
    assert r['subjects_with_at_least_one_unambiguous_window'] == 0


def test_source_namespace_and_strict_boundary():
    r = screen_courses([sample('x', 2), sample('x', 8), sample('x', 0, 'B'), sample('x', 10, 'B')],
                       [course('x', 2, 8), course('x', 2, 8, 'B')])
    assert r['courses_with_pre_and_post_sample'] == 1


def test_reject_missing_evidence_and_duplicate_samples():
    with pytest.raises(ValueError, match='duplicate sample'):
        screen_courses([sample('x', 0), sample('x', 0)], [course('x', 1, 2)])
    with pytest.raises(ValueError, match='treatment arm'):
        screen_courses([sample('x', 0), sample('x', 10)], [{**course('x', 2, 5), 'arm': ''}])
    with pytest.raises(ValueError, match='finite'):
        screen_courses([sample('x', 0)], [course('x', float('nan'), 5)])


def test_duplicate_subject_time_requires_replicate_policy():
    from microtwin.course_design import screen_courses
    import pytest
    samples=[{'source_family':'A','subject':'p1','sample':'s1','time':1},
             {'source_family':'A','subject':'p1','sample':'s2','time':1},
             {'source_family':'A','subject':'p1','sample':'s3','time':8}]
    courses=[{'source_family':'A','subject':'p1','arm':'drug','start':2,'end':4}]
    with pytest.raises(ValueError,match='duplicate source-subject-time'):
        screen_courses(samples,courses)
