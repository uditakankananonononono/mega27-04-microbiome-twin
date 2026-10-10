# Censoring-aware abstention contract, October 10, 2026

A strict metadata-only assay semantics contract and CLI now represent the actual reason OMM12 quantitative C1 stays locked. No values consumed, no DTL numbers accepted, no conversion/imputation, no distributions/effects/admission.

```sh
PYTHONPATH=src python -m microtwin.cli check-censor-semantics results/omm12_censor_semantics_metadata_20261010.json
```

OMM12 returns ABSTAIN (exit 2): normalization only defined, zero interpretation unknown, missing convention unknown, provenance only method-definition-level. Method statement excludes below-DTL entries; that does not identify which numeric zero representation is true-zero, below-DTL, excluded or missing. Existing successful integrity parse therefore cannot become quantitative admission.

## Contract and validation
Exact fields: schema, unit, normalization, zero_interpretation, missing_convention, DTL_policy, provenance_status. All semantic fields have bounded enumerated labels; no caller-provided numbers/raw values/evidence prose or extra fields accepted. Unknowns never default to valid. Normalized-copy units with not-applicable normalization, below-DTL zero with no applicable DTL, exclusion with censored-flagged policy, and missing-zero encoding block readiness. Declaring zero as below-DTL/excluded/missing blocks quantitative-absence interpretation without conversion. Explicit true-zero/known conventions can produce declaration-ready only, not admitted data.

Synthetic ready path is SEMANTIC_DECLARATIONS_READY_FOR_MANUAL_REVIEW (exit 0), while quantitative_summary_eligible/effect_eligible/C1_admitted remain false. Submitted evidence-reviewed labels cannot authenticate calibration or rights. Loader rejects malformed/duplicate JSON, nonfinite constants, symlink input and size over 10KB with a fixed non-echoing error. Standard-library CLI only.

Eighteen tests cover every unknown field, non-true-zero distinctions, numerical/raw/unknown fields, normalization/DTL contradictions, ready-but-not-admitted path, OMM12 abstention and CLI no echo. This is a conservative prerequisite contract, not a general censored-data statistics model. It refuses to automatically analyze even some well-described censoring patterns rather than create undocumented estimators.

Inputs were the already published documentary zero/DTL gate findings only. No private quarantine/source outcome reads, fits/downloads/contacts or claim changes. Quantitative C1 NOT_ADMITTED_LOCKED, C2 BLOCKED, C3 NOT_PROPOSED, useful_win NOT_TESTED remain unchanged.

Code `src/microtwin/censor_contract.py`; CLI `check-censor-semantics`; tests `tests/test_censor_contract.py`; real metadata fixture/output `results/omm12_censor_semantics_metadata_20261010.json` and `results/omm12_censor_semantics_check_20261010.json`.
