"""Outcome-blind eligibility screen for baseline-to-recovery cohorts.

Uses subject, source family, arm, collection time and treatment intervals only.
It never consumes abundance outcomes or converts courses into causal effects.
"""
from __future__ import annotations

from collections import defaultdict
from math import isfinite


def screen_courses(samples, courses, *, min_pre_days=0, min_post_days=0,
                   require_unambiguous_exposure=True):
    """Require strictly pre-start and post-end samples and isolate overlaps.

    Caller must establish source rights and meaning of all times/arms separately.
    Multi-course overlap or an unknown interval is a blocker, not an estimate.
    """
    if not all(isinstance(x, (int, float)) and not isinstance(x, bool) and isfinite(x) and x >= 0
               for x in (min_pre_days, min_post_days)):
        raise ValueError('finite nonnegative margins required')
    samples = list(samples)
    courses = list(courses)
    if not samples or not courses:
        raise ValueError('samples and courses required')
    by_subject = defaultdict(list)
    seen_samples = set()
    seen_coordinates = set()
    for i, row in enumerate(samples):
        key = _key(row, i)
        sid = str(row.get('sample') or '').strip()
        t = _time(row.get('time'), i)
        if not sid or sid in seen_samples:
            raise ValueError('missing or duplicate sample ID')
        seen_samples.add(sid)
        coord=(key,t)
        if coord in seen_coordinates:
            raise ValueError('duplicate source-subject-time coordinate; resolve technical replicate before screening')
        seen_coordinates.add(coord)
        by_subject[key].append(t)
    by_course = defaultdict(list)
    for i, row in enumerate(courses):
        key = _key(row, i)
        start, end = _time(row.get('start'), i), _time(row.get('end'), i)
        arm = str(row.get('arm') or '').strip()
        if not arm:
            raise ValueError('missing treatment arm')
        if end < start:
            raise ValueError('course end before start')
        by_course[key].append((start, end, arm))
    prepost = 0
    overlap_blocked = 0
    missing_samples = 0
    subject_eligible = set()
    for key, events in by_course.items():
        ts = by_subject.get(key, [])
        for i, (start, end, arm) in enumerate(events):
            earlier = [t for t in ts if t < start - min_pre_days]
            later = [t for t in ts if t > end + min_post_days]
            if not earlier or not later:
                missing_samples += 1
                continue
            prepost += 1
            # Other courses after the selected baseline and before the selected
            # follow-up make the specific exposure uninterpretable.
            window_start = max(earlier)
            window_end = min(later)
            contaminated = any(j != i and a <= window_end and b >= window_start
                               for j, (a, b, _) in enumerate(events))
            if contaminated and require_unambiguous_exposure:
                overlap_blocked += 1
            else:
                subject_eligible.add(key)
    return {'status': 'metadata_only_no_outcomes',
            'sample_rows': len(samples), 'course_rows': len(courses),
            'source_subject_keys': len(by_subject),
            'courses_with_pre_and_post_sample': prepost,
            'courses_blocked_by_other_exposure_in_window': overlap_blocked,
            'courses_without_prepost_samples': missing_samples,
            'subjects_with_at_least_one_unambiguous_window': len(subject_eligible),
            'note': 'Eligibility of a window is design-only; rights, controls, taxonomy, adverse events, prognosis and causal inference remain unverified.'}


def _key(row, i):
    if not isinstance(row, dict):
        raise ValueError(f'row {i}: expected record')
    source = str(row.get('source_family') or '').strip()
    subject = str(row.get('subject') or '').strip()
    if not source or not subject:
        raise ValueError(f'row {i}: source family and subject required')
    return source, subject


def _time(value, i):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f'row {i}: finite numeric time required')
    return float(value)
