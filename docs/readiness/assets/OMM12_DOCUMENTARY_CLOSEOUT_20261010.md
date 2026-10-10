# OMM12 documentary closeout, October 10, 2026

Status: DOCUMENTARY CLOSEOUT, NOT ADMITTED. This extends the structural review only. No numeric outcome cells extracted/recorded, no admission, fits or contact. Numeric assay settings, times and metadata identifiers below are definitions, not outcomes. Rights findings from the previous review remain unchanged. This lane pauses for an outcome-admission proposal review before anything numeric opens.

## Resolved documentary mappings and their limits

### Preparation, treatment and controls
2023 Methods, “Generation of bacterial communities”, specifies independently prepared monocultures and separately prepared medium batches for three biological replicates. Eleven monocultures form each dropout; full consortium is the control. Culture conditions specifies three technical wells per biological replicate, initial inoculum 1:10 into 1 ml medium, 96-h total culture, daily 1:100 transfers, and fresh YL27 supplementation. These establish biological versus technical definitions, not a proven workbook E/S preparation ledger.

207 Tab1 dropout row labels have a full-consortium row sharing the exact batch-token/medium/well suffix. The JSON records those proposed control keys as SYNTAX_MATCH_ONLY. None is certified as physically paired. S1new remains a separate observed token. Matching a technical-well number is insufficient to establish biological-control pairing or statistical independence. Repeated identifiers across Tab1/3/4 are already logged; no distinct experiment is invented.

Methods establish medium intent: AF and APF differ in carbohydrate sources; APFmod leaves out inulin/xylan/mucin, with separate inulin or xylan addition variants. NaOH is added to full consortium and HCl to the I48 dropout for pH followups. Workbook GAM versus methods modified GAM is a documentary candidate alias, not an admitted exact formulation crosswalk. APFI and S/E token variants still lack a definitive source-key map.

### Identity candidate, not applied correction
The JSON maps all twelve strain tokens to the 2022 Methods species/DSM statements. Eleven DSM strings agree with the 2023 Table1 record. YL44 is DSM26127 in 2022 but DSM26109 in 2023; YL45 is DSM26109 in both. Proposed candidate correction: YL44 -> DSM26127, supported by the 2022 original Methods. It is explicitly CANDIDATE_CORRECTION_NOT_APPLIED. Do not merge YL44 with YL45. YL2 species wording differs between publications; DSM agreement does not certify a taxonomic synonym. No strain-token/species alias is used for an admitted join.

### qPCR units, DTL definitions and physical split
2023 Results explicitly describes day-4 culture readout as normalized 16S rRNA copies per ml culture. Methods uses 5 ng gDNA, plasmid standards, strain-specific efficiency and absolute copies per 5 ng gDNA before normalization by strain-specific 16S copy number, sample gDNA concentration, elution factor and sample volume. Below-DTL values are excluded. This resolves the definition and prevents treating readouts as uncorrected cells/ml or replacing excluded values with zero. No numeric strain-specific DTL, efficiency/factor dictionary or row-level censor encoding was recovered from allowed labels/methods. In vivo normalized denominator is not explicitly bound to workbook rows; weighing gut content does not prove copies/g without the normalization map.

2023 Culture conditions states each full 1-ml culture is centrifuged: frozen pellet and retained supernatant for pH/metabolomics. Thus physical pellet/supernatant origin is documented at method level. It does not establish which workbook E/S/AA/SCFA keys refer to the same preparation, well or aliquot.

AA AF/APF label normalization gives 77 distinct E keys, of which only 75 match collapsed Tab1 E keys. AA has I48/APF/E1 and YL44/APF/E1 absent from Tab1; Tab1 I48/APF/E3 lacks an AA key. This is structural mismatch, not numerical disagreement. SCFA uses S/W, pH uses no E in sample keys and numbered columns, so positional cross-assay pairing remains unsupported. Tab12 has 24 distinct sample labels each repeated twice, no distinguishing identifier; do not count those 48 rows as 48 independent cultures.

### Chemistry definitions and units
Untargeted profiling represents feature abundance by integrated peak areas. It uses positive/negative mode, annotation by exact mass/MS2 references, pooled QC every tenth run, randomized spent-media injection order, QC batch control and feature filtering with >80% NA for a specified Bray-Curtis analysis. These are documented processing definitions, not retained-sample QC proof or identification certainty. Workbook2 pvalue/meandiff are derived outputs, not raw concentration or independent biological replicate data.

Targeted SCFA methods uses 3-NPH, isotopic standards and MRM, but the headers/methods do not bind final concentration units, specimen mass normalization, LOD/LOQ or QC status to workbook values. AA and bile acid output units likewise remain unbound. Tab12 explicitly labels polysaccharides g/l and g/L and methods identifies inulin/fructan and acid-hydrolyzed xylan/xylose kit assays. Tab16 labels mouse/cecum weight g and ratio %. LCN2 methods uses duplicate assay wells and an ng/ml standard series, but a standard unit does not prove the final specimen-normalized workbook unit. Histopathology rubric is an ordinal endpoint, not quantitative chemistry.

### Mouse experiment and population map
2023 Mouse experiments establishes C57Bl/6J full/KB1/I48/YL58 groups, two inoculations 72 h apart and terminal day20 harvest; DNA specimens are weighed intestinal contents stored at -20 C, and cecal metabolomics uses separately snap-frozen weighed content at -80 C. Methods describes ileum/cecum/colon/feces. Workbook also has Je labels, and LCN2 Jejunum header; retain those as observed, without inventing an omitted collection method.

The JSON preserves 179 region-specific sample identifiers and mouse-ID/condition/sex metadata from the selected endpoint tables. TV287/TV293/TV295 and D20 are observed experiment/time tokens, not a recovered cage map. Endpoint overlaps from the structural report remain label-level, not aliquot equivalence. Duplicate assay wells, repeat gut regions and longitudinal LCN2 feces remain nested within animal, not independent mice.

NEW CONFLICT: TV293 mouse label 2546 is OMM12 in cecum (Tab13 A64) but OMM-KB1 in feces/ileum/jejunum (A100/A119/A138). Tab14 repeats the same identifiers. A single-treatment-per-mouse map fails. Preserve all observed mappings and mark the treatment identity unresolved; do not fix a presumed typo or claim exact valid group n. Previously reported distinct-ID counts are per-condition row labels only, not certified allocation counts.

## UNRESOLVED register
Full machine-readable register in `omm12_documentary_closeout_20261010.json`, each with status UNRESOLVED and specific evidence gap:
- U1 E/S/S1new biological preparation identity and cross-medium pairing: no token-to-inoculum ledger.
- U2 missing-well reasons and reused-label provenance: no per-sample exclusion/repetition log.
- U3 cages/individual ages/independent cage count: group housing and age ranges only, no allocations.
- U4 randomization: Mice random assignment versus Statistics not randomized. MS injection-order randomization is a separate layer.
- U5 exact old-source/deposit overlap: shared platform/cross-citation; old SI HEAD timed out, no old outcomes opened.
- U6 strain correction/taxonomic aliases: original papers disagree on YL44 DSM; candidate correction not applied.
- U7 DTL/calibration/censor encoding, assay units/QC: definitions and settings do not supply endpoint-bound numeric dictionaries.
- U8 physical assay pairing/repeated polysaccharide rows: label mismatch and no E/S ledger or repeat distinction.
- U9 mouse2546 treatment conflict: region labels disagree; no verified correction.
- U10 frozen endpoint/aggregation/baseline/split/useful-win/compute admission protocol: not commissioned here.

No remaining gap was filled by inference. A separately reviewed outcome-admission proposal must choose a defensible restricted scope or resolve these gaps before outcome opening; this closeout does not authorize the next step.

## Sources
2023 Methods/Results: https://www.nature.com/articles/s41467-023-40372-0

2023 strain table: https://www.nature.com/articles/s41467-023-40372-0/tables/1

2022 Methods identity/protocol comparison: https://www.nature.com/articles/s41396-021-01153-z

Inspected workbooks: https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41467-023-40372-0/MediaObjects/41467_2023_40372_MOESM3_ESM.zip

Deposit lineage: https://massive.ucsd.edu/ProteoSAFe/dataset.jsp?accession=MSV000090704
