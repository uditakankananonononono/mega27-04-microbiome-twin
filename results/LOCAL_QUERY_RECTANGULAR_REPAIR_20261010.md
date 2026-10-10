# Query parsing correctness repair, October 10, 2026

Demonstrated defect: local query matrices bypassed research intake and used a separate pandas reader. A header sample_id,A with row PRIVATE_QUERY,1,1 silently inferred the first field as an index and emitted a prediction under sample ID 1. The prior intake repair protected training/calibration inspection, not this query path.

Repair: the shared local prediction reader now uses strict rectangular logical-record validation and explicit no-index inference. This propagates to baseline, checked-contract and calibrated prediction paths, including secondary table reads. No numerical formula, model selection or valid scientific result changed. Fixed privacy-safe errors replace malformed row/quote diagnostics.

Regressions: excess/missing fields and unclosed query quotes, no CLI output file on failure, calibrated-route refusal, and valid quoted query ID preservation. Targeted prediction/calibration/intake suite: 34 passed. Full fresh suite and exact remote-head guarded publication are reported separately. No source gates, biological forecasts, manuscript or raw data changed.
