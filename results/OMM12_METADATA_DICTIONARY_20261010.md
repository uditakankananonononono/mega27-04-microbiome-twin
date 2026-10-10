# OMM12 source-data inventory and methods dictionary, October 10, 2026

Status: INVENTORIED, NOT ADMITTED. Authorized publisher ZIP downloaded and central directory inspected; no workbook extracted or opened, no qPCR/metabolite value or outcome matrix inspected/analysed, no fitting, no author contact. Dictionary is publication-level, not an exact workbook sample map. Nasal/hCom/oral leads and Wastyk remain untouched.

## Archive and rights
Observed publisher source-data link: https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41467-023-40372-0/MediaObjects/41467_2023_40372_MOESM3_ESM.zip

Actual download: 1,195,857 bytes, SHA256 45157de4fd55eacdaf662785d376b170f6d8711984d4ab777635f61fe7d6d81a. Four paths, total uncompressed 1,214,956 bytes:
- source-data_table_2_revision.xlsx: 1,063,232 bytes (compressed 1,049,920).
- source-data_table_1_revision.xlsx: 151,236 bytes (compressed 144,681).
- Two __MACOSX resource-fork paths, 244 bytes each. No scientific meaning assigned.

Full path/size/CRC inventory: omm12_source_zip_inventory_20261010.json. No README, LICENSE or COPYRIGHT-named member. No member extracted/read, so absence of a standalone license is NOT proof there is no workbook-embedded rights note. Nothing contradictory found; embedded rights remain unchecked. A later permitted workbook metadata read must stop on contradictory rights before scientific opening.

Exact publisher declaration at https://www.nature.com/articles/s41467-023-40372-0 : 'This article is licensed under a Creative Commons Attribution 4.0 International License, which permits use, sharing, adaptation, distribution and reproduction in any medium or format, as long as you give appropriate credit to the original author(s) and the source, provide a link to the Creative Commons licence, and indicate if changes were made.' The page adds: 'The images or other third party material in this article are included in the article’s Creative Commons licence, unless indicated otherwise in a credit line to the material.' Data availability declares all supporting data within paper, supplementary information and source-data table files. This supports the publisher-provided-source route, subject to any credited exclusions; it does not certify unopened workbook notes.

MassIVE pairing: https://massive.ucsd.edu/ProteoSAFe/dataset.jsp?accession=MSV000090704 explicitly '[dataset license: CC0 1.0 Universal (CC0 1.0)]'. Its record cites both the 2022 OMM interaction paper and 2023 dropout paper. Archive/publication versions may share data; do not treat the two publications/deposit as independent replications. No MassIVE files downloaded.

## Publication-level dictionary
| Dimension | Evidence | Remaining exact-map requirement |
|---|---|---|
| Community | OMM12 full consortium, twelve individual OMM11-x dropouts | Workbook condition keys and verified removal success |
| Culture replicate | Three biological inocula from independently prepared monocultures and separately prepared medium batches | Batch/inoculum labels and whether shared across media/control |
| Technical replicate | Three wells per biological replicate, nine wells total | Well-to-inoculum nesting; do not count wells as independent cultures |
| Exposure/time | 96-h culture; 10 microlitres transferred into 1 ml fresh medium every 24 h; initial inoculum diluted 1:10; M. intestinale added to inocula to improve growth | Exact full-control/dropout/batch/day mapping; spike consistency |
| Main dropout environments | AF glucose versus APF sugar mixture/polysaccharides, same background basis | Actual medium keys and batch pairing |
| Other environments | mGAM glucose/starch; TYG glucose; YCFA glucose/starch/cellobiose; modified APF removes polysaccharides or adds inulin/xylan | Distinguish primary dropout screen from selected mechanistic follow-ups |
| Culture target | Day-4 strain-specific qPCR, normalized 16S copies/ml; cell pellet and matched supernatant after culture collection | Exact sample IDs, normalized units, missing/DTL flags and physical pairing |
| qPCR method | 5-ng gDNA; strain-specific primers/probes; plasmid standard curves; strain-specific detection limits; normalized by 16S copies, gDNA concentration, elution factor and sample volume | Numeric DTL/calibration dictionary, normalization factors, censor convention; do not substitute zero |
| Mouse groups | Full consortium versus E.fa/B.ca/B.co dropouts, two inoculations 72 h apart, 20-day terminal harvest | Individual mouse/sex/age/cage/inoculum/region/assay map |
| Mouse nesting | Both sexes, age 6-20 weeks; 2-6 mice/cage, not single-housed | Cage allocations and independent cage/inoculum count; repeated gut regions share mouse |
| Mouse endpoints | Ileum/cecum/colon/feces qPCR, cecal metabolomics, selected histology/LCN2 | Per-endpoint eligibility and consistent specimen/aliquot keys |
| Chemistry | Targeted 3-NPH SCFA assay with isotope standards; untargeted MS pairing exists | Actual concentration units/wet-dry normalization/QC/analyte/limits not bound to workbook |
| Randomization | Mice section says animals randomly assigned; Statistics says experiments not randomized | Preserve contradiction; cannot call randomized until reconciled |
| Blinding | Except histopathological scoring, investigators not blinded; no sample-size predetermination; no data exclusions stated | Exact workflow/assay allocation evidence if needed |

### Exact n evidence, not guessed reconciliation
- Culture methods: 3 biological replicates x3 technical wells =9 wells. Full-consortium Fig1 AF/APF N=9, mGAM/TYG/YCFA N=6; interpretation/nesting of N=6 is not explicitly reconciled by those captions. Do not infer two biological replicates solely from 6/3.
- Twelve-dropout AF/APF screen Fig1D and metabolomics Fig2: N=3 replicates per condition. Likely biological summaries, but exact raw-well-to-batch map unopened; no n inflation.
- Fig2 pH caption N=9 each; must reconcile to methods' 3 biological x3 technical, not nine independent preparations.
- Mouse Fig5A N=8-10 mice/group; Fig5B/C N>=8/group, not exact per-group counts. Full, E.fa, B.ca and B.co group counts therefore remain individually UNVERIFIED, not invented as 8/9/10.
- Fig6 weight N>=8/group; histology N=5/group; LCN2 N=5/group; metabolomic panel N=5/group. Counts are endpoint-specific and not additive; whether identical animals contribute requires map.

### Strain identity dictionary (published Table1, no silent correction)
Source: https://www.nature.com/articles/s41467-023-40372-0/tables/1

C.in: Clostridium innocuum I46, DSM26113; B.ca: Bacteroides caecimuris I48, DSM26085; L.re: Limosilactobacillus reuteri I49, DSM32035; B.an: Bifidobacterium longum subsp. animalis YL2, DSM26074; M.in: Muribaculum intestinale YL27, DSM28989; F.pl: Flavonifractor plautii YL31, DSM26117; E.cl: Enterocloster clostridioformis YL32, DSM26114; A.muc: Akkermansia muciniphila YL44, DSM26109; T.mu: Turicimonas muris YL45, DSM26109 AS PRINTED; B.co: Blautia coccoides YL58, DSM26115; E.fa: Enterococcus faecalis KB1, DSM32036; A.mur: Acutalibacter muris KB18, DSM26090.

The published table repeats DSM26109 for A.muc and T.mu. Do not infer the correction, merge them or use that identifier as an exact strain join. Species labels/strain labels need an original-source identity reconciliation before admission. No oral HACEK or named Desulfovibrio/Bilophila/Desulfobulbus appears in this twelve-strain table; broad oral/sulfate-family tests are not supported by this panel. Anaerobe trait variation has not been mapped; anaerobic cultivation does not establish usable variation in a trait predictor.

Medium dictionary source: https://www.nature.com/articles/s41467-023-40372-0/tables/2 . Primary methods and captions: https://www.nature.com/articles/s41467-023-40372-0 .

## Predictor/target proposal, not scoring authorization
A separately reviewed task could test a locked baseline-only rank against measured day-4 community change caused by each removal, using the full consortium as matched control within medium/biological batch. Exclude the deliberately absent taxon from a remaining-community disturbance endpoint, otherwise perfect removal detection can masquerade as ecological prediction. Freeze treatment/control aggregation and missing/DTL rules before targets. Absolute qPCR-copy target is not a taxonomic relative-composition target; no automatic conversion to microbial cell load.

Candidate predictors: species presence/strain traits known before removal and an admissible baseline/control-only composition or network. Current archive may contain only terminal outcomes, not unperturbed longitudinal predictor histories. Fitting a network to post-dropout targets then ranking removals would leak. Training/control use, score transfer across media, taxonomic translation and same-task comparator eligibility need their own reviewed design. Twelve taxa/three biological batches constrain rank precision; nine wells do not fix it. Mouse three-dropout arm is selected follow-up, not all-taxon confirmation.

Useful direct endpoint: rank predicted removal impact versus matched absolute changes in remaining taxa, with abundance/prevalence-only and noninteraction controls. Could falsify an ecological interpretation of ridge/literature-proxy rank only if enough exact trait/taxon coverage and baseline support exist. Does not validate the NASA Blautia assay discrepancy, a universal anaerobe law, clinical response or a leading-tool win by itself.

## Subsequent admission review would need
Separately permit restricted workbook structural/header/metadata inspection that prevents numeric outcomes from entering review; verify any embedded rights first. Recover worksheet-to-experiment identity, exact biological/technical nesting, species/strain correction, control/dropout/medium/day keys, endpoint populations and DTL/unit dictionaries. Reconcile mouse randomization text, cage unit and per-group n. Confirm mirror/2022 overlap and compare to previously exposed source families. Any outcome opening or fitting remains a separate reviewed protocol/compute step. This unit stops here with INVENTORIED, NOT ADMITTED; no biological gate closes.
