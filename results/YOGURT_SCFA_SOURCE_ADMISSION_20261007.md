# Yogurt/rolled-oat source admission split

Diet source protocol 56943ab. Public sources only; no author email.

## SCFA deposit: admitted for the narrow first-period development task
Zenodo record 15363886 explicitly labels deposit CC BY 4.0. README binds 462 stool samples, eight SCFA concentrations in micrograms/g and 22 QC duplicates. Concentration workbook has 3,696 unique sample-analyte rows, eight per sample, all Feces/micrograms/g, and matches every metadata sample name. MD5 0198c9ca3134d8829ee7de71a9b0a3c0 matches source deposit. Metadata has 440 Iteration=1 string rows and 22 Iteration=2 string rows. Main rows give 110 submitted subjects, all four phases, unique subject-time coordinates. Publication defines four-week washout/baseline and four-week yogurt / yogurt+oats crossover periods (250 g yogurt daily, additional 50 g oats daily). Group A yogurt first, B combination first.

Collection metadata are not perfect: T1-T2 ranges 24-138 days; valid T2-T3 pairs include two nonpositive intervals (minimum -330 days) and two pair endpoints are unparsed; T3-T4 valid intervals 28-33 days. No date repairs. Frozen first-period protocol uses only T1/T2 with 21-35-day interval. Exact dose onset/adherence is not measured by these labels. SCFA and metagenomics use different stool containers (native vs ethanol-stabilized); common submitted IDs alone do not prove same physical aliquot.

## GitHub taxonomic tables: metadata-only, rights unresolved
Current author repository redirects to IPE-Freiburg/Yogurt_rolledOat_Microbiome, tree 6fdcb68179c1b12399b5f9e40164bdf5aac09037. Contains small species/SGB tables and metadata, but no specific data reuse license in inspected tree or repository metadata. Article CC BY is not automatically a GitHub participant-data license. No taxonomic outcome file opened. Microbiome metadata workbook has wrong A1:A1 dimension; read-only reset_dimensions reveals 440 main samples/110 submitted subjects, no duplicate subject-time/missing required IDs. Scripts bind group/phase and include illustrative participant clinical records; do not forward or publish those records. Current primary accession PRJNA1258884 differs from truncated README PRJNA125884; preserve mismatch and use primary identifier.

SCFA unit remains same-study development, not certified unseen-source biological replication or validation of a taxonomic model. Exact-accession/mirror independence from archived 160 studies has not been certified and is not claimed.

Sources:
- https://pmc.ncbi.nlm.nih.gov/articles/PMC13084677/
- https://github.com/vstanislas/IPE_yogurt_rolledOat_microbiome
- https://zenodo.org/api/records/15363886
- https://zenodo.org/records/15363886
- https://zenodo.org/api/records/15363886/files/README.md/content
- https://zenodo.org/api/records/15363886/files/SCFA_metadata.xlsx/content
- https://zenodo.org/api/records/15363886/files/Metabolon_FREI-0301-21TASA%20CDT.xlsx/content
- https://zenodo.org/api/records/15363886/files/FREI-0301-21TASA%20Sample%20Analysis%20Report.pdf/content
- https://www.ncbi.nlm.nih.gov/bioproject/PRJNA1258884/
