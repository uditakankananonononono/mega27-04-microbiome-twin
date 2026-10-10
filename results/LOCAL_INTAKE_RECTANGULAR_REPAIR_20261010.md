# Local intake rectangular-record repair, October 10, 2026

Demonstrated defect: a samples-by-taxa TSV with two header fields but three fields in every data record passed schema validation. pandas silently inferred the first field as an index, shifting sample IDs and numeric values. This could validate the wrong biological table rather than raise an error. Uneven records also exposed raw parser diagnostics.

Repair: a strict CSV-record pass checks each logical record against header width before pandas parsing, including subject maps. Duplicate headers, malformed quoting, unreadable text and parsing failures return fixed errors without private paths/values/parser details. Quoted delimiters remain supported. pandas is explicitly instructed not to infer an index. Existing 50 MB input limit, rights-declaration caveats, grouping semantics and no-clinical/no-external-validation boundaries remain unchanged.

Regression tests cover excess fields on every record (the silent-index case), missing fields, mixed-width records, unclosed quotes, subject-map variants and valid quoted delimiters. Targeted intake suite: 11 passed. Full fresh suite and guarded push/readback are reported separately. No archived biological result, source gate, paper or raw data changed; this is local-platform correctness, not scientific validation.
