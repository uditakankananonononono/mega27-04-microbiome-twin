# Baxter harmonization provenance: partial population reconciliation

Rodriguez et al. 2023 provides curated 16S reads, metadata and taxonomic tables from 11 fiber studies, reporting 2,368 specimens and 488 subjects. Its Table 2 reports Baxter_2019_V4 as **175 subjects and 1,205 samples**, not the 174 analyzed participants in the original Baxter article. This corroborates the 175 subject keys in our ENA census and the 1,205 sequencing-run inventory. It does not establish that all 1,205 are unique stool specimens: our accession inventory has 1,201 unique samples. The curated table's number must not replace an exact specimen/run crosswalk.

The metadata dictionary defines subject_id as a person key, sampleid as a fastq-file name corresponding to a fecal sample, sample_id_2 as an original sample ID, timepoint as before/after, and timepoint_numeric as chronological ordinal. An ordinal is not elapsed days. time_days is elapsed time since intervention if known. Multiple naming layers require an explicit mapping before joins, not case-folding or guessing. No SCFA columns or sentinel semantics are defined by this shared dictionary.

Author processing code is MIT-licensed. A bounded inspection of the potato-arm R Markdown source identifies references to separate subject/sample naming layers and an endpoint contrast at before_1/after_8, with pair filtering. That is a distinct reanalysis rule, not evidence resolving the original minimum-three-samples-per-phase SCFA population. The code also contains downstream descriptive results: these are viewed source content, not an independent confirmation. We did not execute it, download its participant inputs, or use its reported effects to select a model.

The official Figshare descriptor lists CC0 and one archive, Data_submission.tar.gz, 18,690,317,561 bytes. No archive or raw sequencing file was downloaded. This is a reused curation source and belongs to the original biological source family; it adds no independent cohort. Public documentation partially explains why 175 appears in a deposit-oriented population, but not which participant was excluded from 174, why our literal >=3-per-phase specimen count is 143, or how chemical missing/sentinel values should be interpreted. Admission remains pending. Useful predictive win: not evaluated. Independent validation: false.

## Sources inspected
- Primary descriptor https://www.nature.com/articles/s41597-023-02254-4
- Population summary https://www.nature.com/articles/s41597-023-02254-4/tables/2
- Shared metadata dictionary https://www.nature.com/articles/s41597-023-02254-4/tables/3
- Author repository README/license overview https://github.com/cirodri1/fiber-data_records
- File inventory https://api.github.com/repos/cirodri1/fiber-data_records/git/trees/main?recursive=1
- Bounded code source https://raw.githubusercontent.com/cirodri1/fiber-data_records/main/4_Alpha_Beta_Diversity/Baxter_2019_V4/potato_alpha_beta.Rmd
- Deposit license and archive descriptor https://api.figshare.com/v2/articles/21295352
- Tool-returned public deposit URL https://springernature.figshare.com/articles/dataset/Curated_and_harmonized_gut_microbiome_16S_rRNA_amplicon_sequences_metadata_and_OTU_tables_from_dietary_fiber_intervention_studies_in_humans/21295352

Next source-level choices: keep this cohort pending and seek a directly downloadable measured-panel source; or separately authorize a bounded targeted archive/header investigation to learn whether small metadata can be extracted without transferring 18.7 GB. Neither choice permits a model fit now. A range request to a compressed archive is not assumed to provide random access, and no such request is issued under this unit.

## Routing decision, 7 October 2026 23:02 IST
Parent accepted the recommendation to park Baxter and seek an alternate directly downloadable measured panel using free/public, metadata-only research. No budget is assigned to the 18.7 GB archive or a header/range investigation. The source is pending admission, not rejected as scientifically unusable, and the 175/174/143 distinction remains recorded. Do not rerun this source's census or fit it under the alternate-source task.
