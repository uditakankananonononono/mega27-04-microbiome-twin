# Benchmark unique-field JSON repair, October 10, 2026

Reproduced defect: conflicting duplicate model keys silently selected the last validation vector and produced a frozen comparator record. Validation/test errors, selection receipts and model-file mappings now reject duplicate JSON fields at every depth, as well as malformed UTF-8/syntax, using fixed private-safe diagnostics. Complete-model, validation/test separation and unauthenticated-timing boundaries remain. No numerical inference or biological result changed.

Four new regressions cover duplicate validation vectors, test vectors, selection fields and model-file mapping paths. No output on refusal; private values omitted from diagnostics. Full fresh guarded suite and exact publication readback reported separately. This is submitted-evidence parsing integrity, not source authentication or benchmark success.
