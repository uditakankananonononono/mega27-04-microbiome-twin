# Amendment 1 to PREREG_twindiscovery.md — completion-order stopping rule

Locked 2026-09-26 07:12 IST, BEFORE opening any T1 score output (no genus
out-strength value, consensus table, or test statistic has been read; only
per-study completion counts were monitored as progress metadata).

Context: per-study GraphTwin training on saturated shared CPU is slower than
planned (~2 studies/hour/shard). Full 124-study coverage will not complete
before the 2026-09-26 13:00 IST delivery deadline.

Locked rules:
1. Shards stop accepting new studies at 09:30 IST 2026-09-26. Any study whose
   partial rows are written by then is in the analysis set; in-flight studies
   are discarded (their rows either fully exist or do not; the script writes
   a study's rows atomically after fitting).
2. The analysis set is ALL completed studies. Completion order is manifest
   order modulo shard index (ei % 2), which is fixed ex ante and independent
   of study content, so the stop introduces no outcome-dependent selection.
3. The T1 Fisher/binomial test (construction unchanged from the main prereg)
   runs on this set with n_studies and coverage % reported alongside q.
4. If coverage < 50% of eligible studies, the paper reports T1 as
   "partial-coverage replication" with the exact study count; the claim
   wording is softened accordingly and the limitation is stated.
5. All other prereg terms (scorer, test construction, BH q < 0.05 success
   threshold, redirect clauses, negatives-reported policy) are unchanged.
