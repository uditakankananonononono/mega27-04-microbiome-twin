# CEREMI source admission note (2026-10-07, outcome-blind)

Protocol: results/PREREG_20261007_ceremi_admission.md. No abundance values opened; no models run.

Findings (metadata only):
- PRJEB28341 (2019 AAC, 16S): ENA read_run sample_alias/sample_title are opaque codes (e.g. 028-KMXE). No subject ID or sampling day in ENA fields queried.
- PRJEB58157 (shotgun): aliases CER_001.. (subject-like) but no day field in queried fields; multiple runs per alias.
- No directly retrievable processed abundance table located; 2019 supplement is behind the ASM DOI.
- Exposure: family was previously read at metadata/publication level; exposure check from parent still pending.

Verdict: NOT ADMITTED for outcome opening. Failed criteria: sample-day mapping and processed table not verified. Reopen only if a mapping file (supplement or authors) is found and the exposure check returns.

## Addendum (2026-10-07, post-admission check)

- Exposure: CEREMI is treated as publication-level exposed (two published analyses, PMC6535507 and Microbiome 2024, doi 10.1186/s40168-023-01746-0). It is not certified untouched.
- Mapping check: the fetched 2024 Microbiome article text has references to Supplementary Tables S1-S7 and Figure S1 only. It has no data-availability section, no ENA accession and no sample-to-subject/day mapping in the text we could read. No supplement file was opened.
- Verdict unchanged: NOT ADMITTED. No abundance values opened, no models run.
- Next: move to the next open cohort with an explicit subject/day mapping, protocol frozen first.
