# Paired report export rectangular repair, October 10, 2026

Reproduced defect: an extra leading field on every loss record silently became a pandas index; shifted sample/subject/fold fields then matched a different valid partition manifest and passed submitted-label checks. Both loss and partition files now use strict rectangular logical-record parsing before numeric conversion. Invalid numeric loss errors are fixed and omit private cells. Existing hashes, exact outer-test matching, partition boundaries and submitted-only limitations remain.

Seven new regressions cover loss/partition extra fields, unclosed quoting, invalid UTF-8 and nonnumeric private loss values. Targeted suite 19 passed. No model runs, actual independence certification, biological gates, paper or archived scientific results changed. Full guarded publication reported separately.
