# MTBLS6771 bounded documentary inventory, October 10, 2026

Decision: NOT ADMITTED UNDER PUBLIC ACCESS GATE. The single approved documentary unit is closed. No source substitution or future monitoring. Access failure is not evidence the deposit lacks files, is invalid or fraudulent.

## Scope and attempt
One public metadata/method/identity/structure inventory of the 2024 CEREMI author's metabolomics pointer, <=20 MB transfer, <=50 MB local/extracted files, <=30 minutes. No outcomes/numeric profiles, fits, source requests, sign-in, registration or paper/Drive changes. No FTP or alternative owner-access bypass attempted after the explicit owner-only restriction.

The original page https://www.ebi.ac.uk/metabolights/MTBLS6771 resolves to the MetaboLights editor. A native HTTP page request returned the application shell (117,317 bytes), not a study inventory. The cloud browser finished loading and displayed:
- MTBLS6771 Submission Not Yet Complete.
- Study currently being processed or has not completed initial validation/setup.
- Study processed by curators or in a provisional state; access restricted to study owners only.

The documented public API routes for study metadata and file inventory both returned HTTP 401 with message 'User has no permission to execute.' No files, sample tables, assay maps, protocols, headers or outcome rows were recovered. Sign-in is not a remedy for owner-only source permission, and none was attempted. Browser outcome recorded and session released.

## Field-level table
| Required field | Decision | Evidence |
|---|---|---|
| Author pointer to accession | PASS at publication level | Previously verified CEREMI 2024 data availability names MTBLS6771. This does not prove released public access. |
| Public inventory accessibility | FAIL in this attempt | Live owner-only/provisional UI plus two public API 401 responses. |
| Exact primary deposit identity/content | UNVERIFIED beyond accession | No accessible study title, file inventory or metadata describing actual deposited assays. |
| Participant/specimen/day/arm longitudinal mapping | UNVERIFIED | No sample or assay metadata retrieved. |
| Processed longitudinal abundance table | UNVERIFIED | No inventory or matrix headers retrieved; this metabolomics pointer cannot be assumed taxonomic abundance. |
| Compatible measured targets | UNVERIFIED | No analyte/unit/QC metadata retrieved. CEREMI article describes untargeted relative metabolomic signals, not automatically compatible fecal-SCFA concentrations. |
| Specific data reuse/normalization/QC | UNVERIFIED | No deposited data/license/assay schema inspected. Article license alone does not establish unavailable deposit content rights. |
| Physical multimodal pairing | UNVERIFIED | No retrievable specimen/aliquot/time binding. |
| Lineage/exposure | Same CEREMI family; external independence UNVERIFIED | Author-declared pointer from already-exposed 2024 paper. No new recruitment or untouched-source status inferred. |
| Same-task comparator or scoring feasibility | UNVERIFIED | No admitted data/task contract. No scoring plan or fit authorized. |

## Observed sources
- Entry: https://www.ebi.ac.uk/metabolights/MTBLS6771
- Final live UI: https://www.ebi.ac.uk/metabolights/editor/study-not-completed?studyIdentifier=MTBLS6771&isOwner=false&actions=login,home
- Public metadata API, 401: https://www.ebi.ac.uk/metabolights/ws/studies/MTBLS6771
- Public file API, 401: https://www.ebi.ac.uk/metabolights/ws/studies/MTBLS6771/files?include_raw_data=false
- Official API/file documentation: https://ebi-metabolights.github.io/guides/Files/
- CEREMI primary pointer provenance: https://link.springer.com/article/10.1186/s40168-023-01746-0

Working documentary directory below 1 MB, no extraction, no bulk download; browser subresource overhead not byte-metered. Work completed in under five minutes. No public source files/participant identifiers committed. No numeric matrix or outcome file opened, no models, communication, paper/Drive edit, paid resources or scientific gate credit. The original paper's pointer and today's provisional-access state are recorded separately instead of choosing one as timeless truth.

## Remaining decision
There is no usable longitudinal mapping or compatible target verified by this unit. Separate source work or a contact/request route would require a new reviewed decision; nothing starts from the author's availability statement. Wastyk/SCFA remain user-blocked; Hagan/Palleja/Centella remain outside this unit. Body-text-page certification remains false.
