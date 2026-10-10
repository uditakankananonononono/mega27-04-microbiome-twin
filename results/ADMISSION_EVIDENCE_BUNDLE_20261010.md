# Admission evidence-bundle tamper check, October 10, 2026

A local metadata/documentary evidence receipt now binds four fixed public artifacts: the frozen OMM12 admission proposal, documentary closeout, quarantine certificate and platform boundary-check output. No raw quarantine or source workbook/ZIP is an input role. No outcomes opened or scientific status upgraded.

## Verified checkout commands

```sh
PYTHONPATH=src python -m microtwin.cli receipt-admission-evidence results/omm12_admission_evidence_receipt_20261010.json --evidence-dir results
PYTHONPATH=src python -m microtwin.cli verify-admission-evidence results/omm12_admission_evidence_receipt_20261010.json --evidence-dir results
```

Creation refuses existing output. Verification reports `local_evidence_hashes_and_boundary_match`, quantitative_admission=false and source_outcome_access=false. It hashes exact artifact bytes, reruns the strict metadata-only boundary validator on the certificate, and requires the boundary output to equal the recomputed metadata result. Input roles and filenames are fixed in code, not chosen by caller paths. The receipt embeds hashes/byte counts/status metadata, not document content or numerical cells.

The JSON schema requires exactly these four roles and the fixed envelope. Extra raw payload fields, unknown schema, status changes, malformed/duplicate JSON, altered/missing artifacts, symlinks (including parent-directory symlinks), oversized inputs and mismatch to stored bytes fail with a fixed error that echoes no submitted values or paths. Documentary Markdown roles require recognized titles and valid text; they are hashed public documents, not parsed scientific proof. This is not arbitrary-document classification or detection of every secret placed into prose.

Fourteen positive/adversarial tests cover all four artifact byte changes, missing/symlink/oversize/raw-certificate/status/extra-role/duplicate/schema cases, CLI rejection without leakage and non-overwrite. Source fixture is copied public evidence only; private files and source outcomes are not read by tests or CLI.

## Contract and limitations
The receipt itself states: unsigned local integrity only, not authenticity or scientific validity. Replacing both receipt and accepted files can evade hash comparison. No source workbook, ZIP, private quarantine, numerical admission or biological certification.

This checks a receipt against the current fixed local artifacts, not against a signed external authority. The document hashes do not certify their truth or authorize new work. A caller replacing the code is also outside the local integrity guarantee. Structural C1 remains documentary-only; quantitative C1 locked, C2 blocked, C3 not proposed and useful_win not tested. All ten scientific gaps unchanged.

Code: `src/microtwin/admission_evidence_bundle.py`; CLI integration `src/microtwin/cli.py`; tests `tests/test_admission_evidence_bundle.py`; receipt `results/omm12_admission_evidence_receipt_20261010.json`.
