# CEREMI source admission note (2026-10-07, outcome-blind)

Protocol: results/PREREG_20261007_ceremi_admission.md. No abundance values opened; no models run.

Findings (metadata only):
- PRJEB28341 (2019 AAC, 16S): ENA read_run sample_alias/sample_title are opaque codes (e.g. 028-KMXE). No subject ID or sampling day in ENA fields queried.
- PRJEB58157 (shotgun): aliases CER_001.. (subject-like) but no day field in queried fields; multiple runs per alias.
- No directly retrievable processed abundance table located; 2019 supplement is behind the ASM DOI.
- Exposure: family was previously read at metadata/publication level; exposure check from parent still pending.

Verdict: NOT ADMITTED for outcome opening. Failed criteria: sample-day mapping and processed table not verified. Reopen only if a mapping file (supplement or authors) is found and the exposure check returns.
