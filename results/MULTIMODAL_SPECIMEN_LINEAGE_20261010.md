# Multimodal specimen-lineage preflight, October 10, 2026

New metadata-only library/CLI distinguishes shared subject labels, specimen-label candidates, declared aliquot lineage and repeated technical rows. No outcomes accessed, no biological/clinical admission granted. OMM12 shared mouse identifiers remain unverified specimen lineage.

```sh
PYTHONPATH=src python -m microtwin.cli check-specimen-lineage results/omm12_specimen_lineage_metadata_20261010.json
```

The real metadata fixture returns BLOCKED (exit 2). It contains 60 endpoint-ID rows across SCFA/bile acids/LCN2/histology, 30 shared subject labels: the twenty SCFA/bile animals and separate ten LCN2/histology animals. Specimen and aliquot IDs are null and lineage_verified=false; collection/material are explicitly unknown, not guessed from assay names. Therefore zero cross-modality specimen candidates and zero submitted verified specimen pairs. These are counts of labels, not certified matched biology. Unknown treatment aliases remain as printed; no OMM11-/OMM- renaming.

## Strict contract
Only source, subject, specimen, collection, material, modality, aliquot_group, technical, condition and lineage_verified fields allowed per row; no values or raw payloads. Schema/version/minimum paired count are fixed envelope fields. Unknown modality/field/type, invalid label, duplicate technical record, or verified=true with null specimen/aliquot is rejected without echo. JSON malformed/duplicates/oversize rejected.

A shared specimen label must agree on subject, collection, material and condition. Across modalities its aliquot group must agree and all lineage declarations must be true to count a submitted verified pair. Different specimens in the same source/subject/collection/material/modality create ambiguous joins, not first-match pairing. Technical repetitions of a specimen/modality add repeat-row counts only, not additional specimens. Same subject with different specimens does not pair. Aggregate report contains no specimen/subject IDs or raw values.

Sixteen tests cover synthetic valid/manual-review path; same-subject/different-specimen; collection/material/condition/subject conflicts; aliquot mismatch; technical repeats/duplicates; unknown/raw fields; null-verified contradiction; ambiguous joins; CLI non-leakage; and OMM12 staying blocked.

## Limits
Submitted true lineage flags do not authenticate physical provenance. Metadata-ready remains manual-review-only, physical_aliquot_source_verified=false, outcome_admitted=false, multimodal_validated=false. Unknown or conflicting provenance cannot be fixed by positional joins. This is an executable prerequisite check, not multimodal predictive integration or a resolved AA75/77/Tab12 duplicate conflict. Those culture gaps and mouse2546 remain unchanged; their numerical outcomes were not opened. Sample collection and tissue identity still need original source evidence. No scientific admission boundary or historical result changed.

Code `src/microtwin/specimen_lineage.py`, CLI `check-specimen-lineage`, tests `tests/test_specimen_lineage.py`, real metadata fixture/output `results/omm12_specimen_lineage_metadata_20261010.json` and `results/omm12_specimen_lineage_preflight_20261010.json`.
