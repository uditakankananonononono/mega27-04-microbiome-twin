# OMM12 workbook structural review, October 10, 2026

Status: STRUCTURALLY REVIEWED, NOT ADMITTED. This advances the prior ZIP inventory, not the outcome/admission gate. Two publisher XLSX workbooks opened for structure only. No numeric qPCR, abundance, metabolite, pH, weight, inflammation or histology outcomes extracted or recorded; no fitting, outcome analysis or author contact. Numeric mouse identifiers were read only in explicitly named metadata columns. Counts below count labels, not measurements passing QC or independent biological units.

## Rights-first finding
All string cells were checked for rights/license/copyright notices before structural use; no contradictory note found. Workbook properties/comment parts were checked; no contrary note found. Package inventories have no embedded media, objects, external links, custom XML or VBA payload. No standalone rights member in the ZIP. The publisher page's CC BY 4.0 declaration and credited-exclusion caveat remain the rights basis, not a claim that absence of an embedded note creates a license. Attribute the original authors/source and changes. Source archive SHA256: 45157de4fd55eacdaf662785d376b170f6d8711984d4ab777635f61fe7d6d81a.

## Sheet dictionary
Exact text headers, dimensions, Overview figure links, selected experiment-label groups and main-screen counts are in `omm12_structural_dictionary_20261010.json`. It contains no numeric endpoint cells. Spaces in sheet names are retained.

| Sheet | Structure and admission implication |
|---|---|
| Overview | Maps Tab1-19 to endpoints and figures; not sample provenance |
| Tab1 | 229x14; `16Scorr`, twelve strain tokens, sum; full/12-dropout AF/APF main screen |
| Tab2 | 65x14; selected APFmod, APF-Inulin/Xylan and acid/base followups; E and S labels intermixed |
| Tab3 | 81x14; OMM12dL50 mutant, full and KB1-dropout in AF/APF/GAM |
| Tab4 | 171x14; selected I48/KB1/YL58/full, AF/APF/GAM/TYG/YCFA |
| Tab5 | 61x5; derived culture abundance ratio, medium/probe/three dropout columns, not another independent cohort |
| Tab6/7/8 | pH differences, sample rows and three numbered columns; row identifiers omit E; columns cannot be assigned biological units by guess |
| Tab 9 | 93x18; amino-acid labels; sample strings use E; blank AF/APF controls; N/A text exists; concentration units not in headers |
| Tab10 | 92x12; culture chemistry/analyte labels; Blank and community rows use S/W; S-to-E physical pairing unverified |
| Tab11 | 24x12; colonization, mouse#, ten analyte columns; 20 mouse/condition metadata rows, five each full/KB1/I48/YL58; units unbound |
| Tab 12 | 49x3; Xylan g/l and Inulin g/L; strain/community/Blank E/medium/W strings; followup media need canonical dictionary |
| Tab13/14 | 180x14/13; absolute/relative qPCR headers; identical 179 sample identifiers; same mice/regions, not independent data |
| Tab15 | 61x5; derived mouse abundance ratio by region/probe/three dropouts |
| Tab16 | 38x6; 37 mouse-ID/condition/sex rows; weight and cecum weight in g, ratio in percent; no weights extracted |
| Tab 17 | 25x29; mouse/sex/colonization plus bile acids; 20 metadata rows; units unbound |
| Tab 18 | 11x11; ten mouse-ID/sex/condition rows; feces D0/D7/D14/D20 plus gut regions; repeated within mouse |
| Tab 19 | 25x10, header row5; ten mouse/sex/condition rows and scoring rubric; rubric definitions are not outcome scores |
| Workbook2 AF/APF | 8302x8/10371x8; ID/rtmed/mzmed/annot_ms1/mode/group (AF) or OMM12 (APF)/pvalue/meandiff. Derived comparison output, not replicate-level concentrations; no numerical values used |

## Biological and technical keys: no naive n inflation
Methods specify three independently prepared biological inocula and three technical wells each. E1/E2/E3 and W1/W2/W3 are compatible with that nesting but workbook labels alone do not prove all cross-assay/cross-medium pairs. Main Tab1 has 228 sample labels; it is not a uniform 26-condition x9 grid:
- AF I48 has seven labels; YL32 eight; other AF groups nine.
- APF YL44 has six (E2/E3 only); KB1, YL31, YL58 eight; other ordinary dropout groups nine.
- APF I48 nine labels comprise E2/E3 plus S1new, not E1/E2/E3.
- Full AF has nine; full APF has twelve: E1/E2/E3 plus S1new. Treating S1new as E1 replacement or fourth independent biological preparation is unsupported.

Retain missing well keys as absent, without inventing why. Three numbered pH columns cannot be joined to E by positional inference. AA E rows and SCFA S rows need an original sample/aliquot map. Blank controls and medium modifications cannot be collapsed into full-community controls.

Tab3 shares 35 identifiers with Tab1; Tab4 shares 65. These overlaps prove labels recur, not necessarily byte-identical endpoint values, which were not read. Prevent double counting unless provenance establishes genuinely separate experiments. Every Tab13 identifier occurs in Tab14; relative/absolute encodings are alternate endpoints of the same sample family.

## Mouse nesting and endpoint populations
Tab13/14 parse as TV experiment, D20, region, mouse ID, condition. TV287 has full/KB1/I48; TV293 has all four groups; TV295 has YL58. This is a nonbalanced experiment-by-treatment structure. Regions Ce/Co/F/Il/Je repeat within mice. Cage identifiers and individual ages are absent from these extracted labels. Counts of distinct IDs by region/condition vary: cecum full/KB1/I48/YL58 9/8/9/10; colon 8/6/9/10; feces 8/9/10/9; ileum and jejunum each 8/9/10/10. These are row-key counts, not proof of valid outcome n; the >=8 caption is not a safe universal denominator.

SCFA and bile-acid tables share all 20 mouse identifiers, and all 20 occur in the weight table. LCN2 and histology share ten identifiers, none of which occur in the extracted weight table. Therefore all endpoints cannot be described as a single matched mouse panel. Shared ID is not proof of same aliquot. Preserve OMM11-KB1 vs OMM-KB1 and analogous naming variants until verified canonicalization. Mice-section random assignment versus Statistics not randomized remains an unresolved source contradiction; do not call the dataset randomized. With 2-6 mice/cage in methods, lack of a cage map prevents a supported independent-cage inference.

## Strain identity and older-source lineage
Workbook abundance headers give KB1,YL2,KB18,YL27,YL31,YL32,YL44,YL45,I46,I48,I49,YL58; no DSM identity note found. 2023 Table1 repeats DSM26109 for YL44/YL45. The older primary paper's Methods explicitly lists YL44 DSM26127 and YL45 DSM26109. This supplies an original-source candidate correction, not authority to silently overwrite the 2023 table. Keep strain tokens distinct; a final verified identity crosswalk must record both source versions and the decision.

The 2022 primary uses these same strains/AF platform, pairwise co-cultures, serial passage and substrate manipulation. Its co-culture protocol includes initial sampling then daily qPCR/pH with serial dilution, distinct from the 2023 main 96-h dropout screen. Shared platform does not prove identical samples, but does defeat presuming independent lineage. MassIVE MSV000090704 cites both publications. Exact 2022 workbook sample-key overlap remains unresolved: a HEAD request to the observed SI workbook timed out; no old outcome workbook opened. Do not label publication/deposit mirrors independent replications. No additional download/compute plan proposed as already approved.

## What remains before outcome admission can be proposed
1. Resolve E/S/S1new biological preparation semantics, complete well exclusions/reasons, control/dropout batch matching and repeated identifiers across Tab1/3/4.
2. Bind units, normalization factors, strain-specific DTL/censoring rules, missing-flag meanings, assay QC and chemistry analyte identities to endpoints. Do not use zero substitution. Workbook headers alone do not supply qPCR/ml or chemistry wet/dry normalization.
3. Verify strain identity crosswalk, culture aliquot pairing, mouse experiment/cage/sex/age/specimen map and endpoint populations; preserve unresolved randomization contradiction.
4. Establish exact prior OMM2022/deposit overlap and already-exposed source-family classification. Neither article nor a mirror becomes an untouched holdout.
5. Freeze a reviewed protocol before numeric outcomes: endpoint definitions excluding the removed taxon from remaining-community disturbance, nested replicate aggregation, controls, missingness, baselines/comparator eligibility, split/transfer rules, all negatives and useful-win criteria, and bounded compute plan. Baseline predictors may not be fitted to post-removal outcomes.

This unit authorizes none of those scientific openings. Readiness is partial structural recovery, not admission, fit readiness, causal discovery, clinical validation, hosted platform completion or independent benchmark success.

## Sources
- 2023 primary/methods/rights: https://www.nature.com/articles/s41467-023-40372-0
- Strain table: https://www.nature.com/articles/s41467-023-40372-0/tables/1
- Medium table: https://www.nature.com/articles/s41467-023-40372-0/tables/2
- Inspected 2023 publisher ZIP: https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41467-023-40372-0/MediaObjects/41467_2023_40372_MOESM3_ESM.zip
- 2022 primary identity/design methods: https://www.nature.com/articles/s41396-021-01153-z
- Deposit lineage: https://massive.ucsd.edu/ProteoSAFe/dataset.jsp?accession=MSV000090704
- Observed old SI link, retrieval unverified after HEAD timeout: https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41396-021-01153-z/MediaObjects/41396_2021_1153_MOESM2_ESM.xlsx
