# OMM12 outcome-admission proposal v1, October 10, 2026

PROPOSED, NOT APPROVED. No numerical outcomes opened by this proposal. Documentary basis: closeout commit 0b9fdb00da3d798357860740651dbad666ab897a. The protocol below is fixed for review before outcome access; acceptance would authorize its audit only, not waive a failed gate or permit fitting. Changing it after outcome inspection requires a versioned amendment and renewed review, never retrospective tuning.

## Decision requested
Approve or reject one bounded numerical source-validation audit of Tab1 culture qPCR only. I recommend allowing the audit as quarantined source inspection, while keeping perturbation-target/model admission blocked unless its documentary gates pass. If a gate cannot pass, the audit ends with NOT_ADMITTED; data availability is not admission. All other modalities remain unopened. No claim of a new discovery or benchmark win follows from the audit.

## Exact proposed access and exclusions
- Source: the already inspected 2023 ZIP, SHA256 45157de4fd55eacdaf662785d376b170f6d8711984d4ab777635f61fe7d6d81a; workbook source-data_table_1_revision.xlsx; Tab1 only.
- Numeric access: B:M (12 strain qPCR columns), restricted to sample rows matching `^(OMM12|OMM11-(KB1|YL2|KB18|YL27|YL31|YL32|YL44|YL45|I46|I48|I49|YL58))_E[123]_(AF|APF)_W[123]$`. These are 222 label-selected rows, at most 2,664 endpoint cells. No sum column, formulas, other sheets or workbooks. Select rows by locked labels, not numerical completeness or attractive effects.
- S1new rows stay unopened/quarantined, not renamed E1 or added as independent n. Include incomplete E-labeled groups in the audit inventory, not necessarily an admitted contrast.
- No numeric AA, SCFA, pH, polysaccharide, bile acid, mouse abundance, weights, LCN2, histology, workbook2 pvalue/meandiff or old-source cells. No raw MS downloads, external downloads, new packages or author contact.
- Budget: local parser over this existing small workbook; one validation pass plus tests; no model training, accelerator or parameter search. A parser/type/provenance failure stops the affected extraction. Preserve source values only in a private quarantine artifact, not public outcome tables or model inputs.

## Frozen admission protocol: OMM12-CULTURE-QPCR-AUDIT-v1

### Stage A: before extraction
Verify exact archive hash, worksheet name, 14-column structure and B:M strain order against the structural dictionary. Recheck workbook rights parts and stop on a contrary restriction. Generate an allowlisted cell-address manifest using labels alone. Record approved protocol version and source-family classification as exposed controlled-culture development source, NEVER untouched external validation. Refuse any cell outside the manifest. Candidate YL44 DSM correction remains not applied.

### Stage B: bounded quarantine validation
Read only allowed cells, preserving raw type and literal missing/error flags. Reject formulas rather than evaluate them; do not read sum as a fallback. Check type, finite/nonnegative numeric representation, duplicate keys, missing/error/zero encodings, and complete nesting inventory. A zero or blank does not become absence/below-DTL by inference. Record technical well availability without filling absent labels. Do not log full outcome matrices to console or publish raw target values. No effect ranking, predictor fitting or effect-driven exclusion is allowed at this stage.

Source-integrity failure (hash/schema/type/duplicate conflict) is NOT_ADMITTED. Passing these checks earns QUARANTINE_VALIDATED only. It does not close biological, normalization, censoring or control-pairing gates. If values expose an issue, report it as an issue, not a scientific result.

### Stage C: admission gates, distinct claim levels
**C1 documentary source-table description:** May be admitted as a bounded description of reported E-labeled normalized-qPCR cells only if units/normalization semantics are adequately tied to that table, missing/zero/DTL conventions are known, strain tokens remain distinct, and integrity checks pass. It can report sample/well coverage and assay-specific distributions. No treatment-effect interpretation, independent biological n, taxonomic cell-load conversion or ecological discovery. If censoring/normalization remains unbound, even this stays NOT_ADMITTED rather than using a convenient default. No cross-source joining based on the candidate DSM correction.

**C2 matched removal-response endpoint:** BLOCKED until E-to-independent-preparation ledger, full/dropout pairing, well exclusions/provenance, DTL/factors and source overlap are resolved. If those are resolved and separately accepted, admit only treatment/control pairs in the same verified biological preparation and medium, with all three technical wells present on both sides and all 12 relevant entries quantitatively valid. Exclude S1new entirely. Freeze exclusion reasons before effects. Select the intersection of complete preparation IDs for each contrast, explicitly report the denominator and missing combinations. Require all three verified independent preparations for any contrast used in a twelve-removal ranking; fewer is coverage-only, not a substituted weak rank. No imputation, pseudocount, omitted dropout hidden as zero, or outcome-selected taxon set.

Predeclared C2 endpoint, if authorized later: within preparation take arithmetic means over the three technical wells; compute remaining-community normalized-qPCR disturbance as sum of absolute dropout-minus-full differences over the 11 retained strain tokens divided by sum of full-control normalized copies for those same tokens. The intentionally removed token is excluded from numerator and denominator to avoid trivial removal detection masquerading as ecological prediction. Undefined/nonpositive control denominator or censoring among required entries invalidates that contrast under this v1 definition. Equal-weight arithmetic mean over the three independently verified preparations is the condition-level endpoint. Record per-preparation values and spread; never treat technical wells as independent n. This endpoint is assay-specific normalized qPCR-copy disturbance, not microbial cell load or clinical benefit.

A complete twelve-removal rank requires all 12 contrasts passing C2 within the same medium and balanced preparation design. Existing nonuniform labels mean that rank is currently BLOCKED, not expected to pass by excluding inconvenient groups. Restricted partial contrasts can be listed for coverage but do not support a complete keystone-rank claim. No significance testing, fit or rank-comparison execution is authorized by this audit proposal.

**C3 predictive/discovery/benchmark claims:** NOT PROPOSED FOR ADMISSION. Even C2 would not validate a twin. Before a later predictive run: freeze pre-removal predictor sources and weights; use no dropout outcome for fitting/feature selection; define same-task abundance-only, no-interaction and existing-method comparators with verified implementability; specify source-family blocked split, uncertainty, all negatives and useful-win threshold before outcomes. No generic or universal top-tool beat from this small exposed culture source. No useful_win=True here; predictive usefulness remains NOT_TESTED. This proposal authorizes none of that future compute.

## What each unopened modality could claim, and why it remains held
| Numerical endpoint | Proposed opening now | Possible later narrow claim | Current barrier and forbidden claim |
|---|---|---|---|
| Tab1 culture qPCR | Stage A/B only; C1 conditional, C2 blocked | Assay-specific source description or verified removal-associated remaining-community response | E/S/S1new, missing wells, control pairing, DTL; no independent rank, causality by label alone, cells/ml, personalized human response |
| Tab2/3/4 culture followups | NO | Verified medium/mutant contrast | Reused keys, selected populations, media aliases and preparation provenance; no independent replication by sheet count |
| Tab5/15 derived ratios | NO | Audit of documented derived summaries | Not separate specimens; no new biological cohort |
| Tab6/7/8 pH | NO | Matched culture environmental-change endpoint | Numbered-column/E map and physical pairing missing; no mediation inference |
| Tab 9/10 AA/SCFA | NO | Paired metabolic response | AA 75/77 mismatch, S/E ledger, units/DTL/QC; no joint mechanism or twin multimodal validation |
| Tab 12 polysaccharides | NO | Verified substrate change | Duplicate labels twice with unknown repeat meaning; no doubled n or consumption inference |
| Tab13/14 mouse qPCR | NO | Region-specific verified animal endpoint | Mouse2546 conflict, cages, experiment imbalance, units/censoring; no valid animal allocation or randomized causal inference |
| Tab16/17/18/19 host endpoints | NO | Verified endpoint-specific phenotype association | Different populations, ages/cages/randomization, units and aliquots; no matched-all-endpoints panel, host predictive validity or clinical claim |
| Workbook2 derived feature summaries | NO | Reproduce source-summary definitions | No replicate-level intensity matrix/QC/sample map; no independent chemical validation or pvalue-based discovery |
| 2022/deposit numeric data | NO | Documented lineage comparison only after separately reviewed plan | Exact overlap unresolved; no untouched or independent validation |

## Ten unresolved gaps bound admission, not just prose
- U1 biological tokens: blocks C2 and any biological-n/rank claim; label-syntax audit only remains possible.
- U2 exclusions/reuse: blocks complete/independent coverage claims and C2; absence remains absence, no inferred reason.
- U3 cages/ages: keeps every mouse numerical outcome out of this proposal.
- U4 randomization: no randomized animal claim. Random MS injection order is not animal allocation and not a cure.
- U5 old-source overlap: source family classified exposed/dependent pending resolution; no external holdout label, even if culture integrity passes.
- U6 identity: candidate DSM26127 kept separate; token-level audit only, no cross-source genomic/trait join until reconciled.
- U7 normalization/DTL/QC: blocks C1/C2 where interpretation depends on it; type checks cannot certify quantitative validity.
- U8 pairing/duplicates: no chemistry/polysaccharide opening or cross-modal claim; do not silently substitute nearest labels.
- U9 mouse2546: all mouse outcomes held, observed assignments preserved; no guessed typo correction or treatment-pooling.
- U10 frozen protocol: this v1 proposes a bounded audit only. Parent acceptance is required before numerical access; later C2 execution/predictive work requires its own reviewed authority and gate evidence.

## Validation outputs and stop conditions
Produce a source-hash/cell-manifest certificate, integrity result, per-gate PASS/FAIL/UNRESOLVED register and separate admitted/quarantined/excluded endpoint list. PASS requires cited evidence, never absence of an error. No successful parse can turn UNRESOLVED into PASS. Unit tests must cover off-manifest access refusal, formulas/errors/ambiguous zero handling, S1new exclusion, incomplete-triplet denial, technical-vs-biological nesting, removed-token exclusion, nonpositive denominator denial and source-family exposed flag. Synthetic fixtures only test computation; they do not validate biological evidence.

If documentary gate evidence is unavailable, report NOT_ADMITTED and stop rather than fit around it. Even a fully validated C1 artifact closes only that restricted assay-description gate. To open C2 later, report the gate evidence and requested scope back for explicit review before aggregation. No deployment, discovery, hosted-platform or fair-leading-tool benchmark gate closes here.

## Sources
- 2023 primary methods/results/rights: https://www.nature.com/articles/s41467-023-40372-0
- 2023 strain table: https://www.nature.com/articles/s41467-023-40372-0/tables/1
- 2022 original methods: https://www.nature.com/articles/s41396-021-01153-z
- Already inspected publisher ZIP: https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41467-023-40372-0/MediaObjects/41467_2023_40372_MOESM3_ESM.zip
- Deposit cross-citation: https://massive.ucsd.edu/ProteoSAFe/dataset.jsp?accession=MSV000090704
