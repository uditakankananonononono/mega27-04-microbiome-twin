# Checked contract ambiguity repair, October 10, 2026

Reproduced defect: duplicate assay fields with conflicting values were silently last-value selected by JSON parsing, and checked calibrated prediction reported matching submitted measurements. This bypassed fail-closed interpretation of ambiguous assay declarations. It never certified actual assay identity.

Two checked prediction readers now share duplicate-field rejection at every JSON object depth. Malformed syntax, invalid UTF-8 and excessive nesting yield fixed errors without private field names/values or decoder details. Existing contract shape/matching and hash checks remain. No model formula or valid numerical result changed.

Four parametrized regressions cover nested duplicate assay, duplicate role, malformed JSON and invalid UTF-8 across direct calibrated and both CLI routes, with no output file on failure. Targeted calibration-contract/assay/conformal tests: 50 passed. The first test run wrongly expected SystemExit from the checked CLI, which returns exit code 2; the assertion was corrected to its existing API without altering production error semantics. No scientific fits or biological gate changes. Full suite and guarded publication reported separately.
