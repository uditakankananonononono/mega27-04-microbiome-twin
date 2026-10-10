# Platform admission-boundary regression certificate, October 10, 2026

A metadata-only consistency validator and CLI now preserve the reviewed OMM12 boundary as an executable check. This is a platform reliability improvement, not new data admission or scientific validation. No raw quarantine or workbook outcomes read, no fits/downloads/contacts, no claim upgrade. The validator accepts this protocol's metadata schema only; other protocols fail closed rather than silently translating statuses.

## Use
From the source checkout:

```sh
PYTHONPATH=src python -m microtwin.cli check-admission-boundary results/omm12_quarantine_certificate_20261010.json
```

The local environment is not installed as a package, so the source-checkout command supplies PYTHONPATH. An installed microtwin package exposes the same `check-admission-boundary` subcommand. A successful command exits 0 for boundary consistency, NOT for quantitative admission. Rejected input exits 2 with a fixed message that does not echo submitted values or file paths.

Result saved as `omm12_platform_boundary_check_20261010.json`. It preserves structural C1 ADMITTED_DOCUMENTARY_REPRESENTATION_COUNTS_ONLY; quantitative C1 NOT_ADMITTED_LOCKED; C2 BLOCKED; C3 NOT_PROPOSED; useful_win NOT_TESTED. Quantitative-admitted, eligible-untouched-holdout and automatic-win flags remain false. Representation counts are representation counts only, not distributions or effect evidence.

## Fail-closed contract
- Strict top-level/nested field allowlists reject raw payloads even alongside otherwise valid metadata. No unknown status or invented protocol accepted.
- Count fields require integers, not booleans; representation totals must match allowed-cell coverage. Manifest requires 222 unique locked-format sample keys and 2,664 unique B:M addresses, twelve ordered strain-column addresses on each unique source row. S1new, sum-column and other-medium keys are rejected.
- Unknown/admitted quantitative/C2/C3/win/holdout labels, malformed counts, missing fields, duplicate keys/addresses, raw nested literals and nonempty issues are rejected without echo.
- JSON loader rejects duplicate JSON members, nonfinite JSON constants, invalid encoding, oversized files and malformed input; maximum read is 1 MB plus a sentinel byte. No workbook/quarantine access is available through this command.
- Synthetic adversarial fixtures test these failures and CLI non-leakage; the already committed OMM12 metadata certificate is the first positive fixture, not newly admitted data.

## Limits
This does not authenticate a grant, rights, provenance, calibration or scientific truth. It checks submitted metadata status consistency; a fabricated but consistent metadata certificate can still be false. It does not recompute the source hash, reread the source or certify that claimed row labels match an original artifact. It does not enforce every other platform command's data access and is not a global security boundary. Existing source-admission/outcome gates remain separate. Review evidence remains required for scientific admission or any amendment. Censoring, normalization, biological pairing and old-source independence gaps remain open, and the ten-gap OMM12 register is unchanged.

Code: `src/microtwin/admission_boundary.py`, CLI integration `src/microtwin/cli.py`, adversarial tests `tests/test_admission_boundary.py`. No historical results altered.
