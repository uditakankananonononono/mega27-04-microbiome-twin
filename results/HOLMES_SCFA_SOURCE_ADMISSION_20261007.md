# Holmes measured-panel source admission: descriptive only

## Locked role and provenance
This is descriptive source admission, not a discovery or prospective evaluation panel. Published outcomes were visible before the pass. At most 28 completed biological participants are the published analysis population; repeats do not expand independent n. Power is not computed, a null cannot establish equivalence, and thresholds will not be re-banded after observing scores. No fitting or numeric chemical analysis was performed.

Holmes2022 documents Duke University recruitment, Duke IRB Pro00087214, NCT03595306 and David Lab specimen processing. Baxter documents Michigan BIO173 recruitment and HUM00094242/HUM00118951. One bounded accession-only comparison finds zero exact sample-accession overlap: 1,201 Baxter samples versus 434 Holmes samples. This meets the agreed standard of accession-level disjointness plus separate recruitment/IRB/processing context for descriptive provenance only. It does not verify person-level identity disjointness. Baxter remains parked after this narrow comparison.

## Design and rights
Six-week, three-period prebiotic crossover: a baseline week before each five-day supplementation week, with stool collected days 3-5 of each week. Inulin and dextrin9g/day, GOS3.6g/day; first day half dose. Six sequence arms assigned sequentially by enrollment, not assumed randomized individual assignment. GC-FID measures acetate, propionate, isobutyrate, butyrate, isovalerate and valerate. Standardized10%w/v preparation and factor10 correction yield mM reported as equivalent mmol/kg by the authors. Six analytes are not the earlier eight-analyte panel or a same-horizon yogurt replication.

Live Figshare descriptors license the public redacted CSV and code CC BY4.0. The all-measures CSV is74,700bytes and directly downloadable. Separate low-replicate-removed and change-score products exist but are not substituted for the source table. One streamed header inspection preceded the metadata census; no participant cells were inspected then. The subsequently frozen one-request census reads metadata in memory, discards concentrations without numeric parsing and retains aggregates only.

## Census and gate failure
440rows/36PIDkeys do not match the paper's413stools/28completedpeople. ID has one distinct value; it cannot be used as a participant key in this public file. The author GLMM code groups byID in its separate input, but that does not establish identity mapping in the redacted all-measures file. PID semantics and exclusion mapping remain unverified.

27rows have missing Arm and Treatment. The other413rows numerically match the published stool count, but this is an untested eligibility hypothesis, not a permitted automatic filter. No PID count after that hypothetical filter was computed. Prebiotic is missing231rows, including expected baseline structure as a plausible explanation rather than a verified interpretation. Named Treatmentlabels contain204baseline and209active rows, with27NArows. All six chemical fields are nonempty440rows; numeric assay validity, censoring and chemical missingness semantics are not tested. No exact sample-accession column joins the440chemicalrows to434sequenced specimens. These populations are not silently merged.

Decision: small-download and explicit-rights gates pass; descriptive provenance standard passes; scientific panel admission remains pending person-key semantics, published analysis eligibility and exact specimen linkage. No training, forecast, clinical or discovery permission follows. The chemical values and participant rows are not stored or redistributed.

## Sources
- Primary https://link.springer.com/article/10.1186/s40168-022-01307-x
- Duke author record https://scholars.duke.edu/publication/1532403
- Original comparator https://journals.asm.org/doi/10.1128/mbio.02566-18
- Deposit descriptor https://api.figshare.com/v2/articles/14502216
- Public dataset https://figshare.com/articles/dataset/Correlations_diet_SCFA_in_vitro_SCFA_response/14502216
- All-measures file https://ndownloader.figshare.com/files/27780411
- GLMM descriptor https://api.figshare.com/v2/articles/14502210
- GLMM source https://ndownloader.figshare.com/files/27780393
- Comparison code https://ndownloader.figshare.com/files/27780444
- Exact accession-only source URLs are retained in results/holmes_baxter_accession_overlap_20261007.json.

Next action is source-code/dictionary-only clarification, not another chemical CSV request or fit. An unresolved key is a blocker to a scientific population, not a reason to rename36publiclabels as28people.

## Bounded clarification outcome and park decision
The remaining Figshare collection descriptors and three small author R Markdown scripts did not supply a public PID dictionary or original eligibility manifest. In-vivo 16S code explicitly states that metadata-processing code is redacted because it contains potentially identifiable information, and loads already processed public objects. Coinertia code similarly withholds raw diet files for privacy. A PID reference in analysis code proves field usage, not its person identity semantics or the mapping of the 440-row public chemical table to 28 completed people/413 stools. No raw personal information was retrieved and no redaction was worked around.

Holmes is now parked for scientific panel admission under the parent instruction to stop if bounded code/dictionary discovery failed. Descriptive provenance passes; scientific admission fails. The observed 36PID/440row versus28/413 discrepancy remains exact, without automatic filtering of the27missing-arm rows. No repeated CSV request, fit or synthetic substitute. Resume an alternate measured-panel source hunt.

Additional code sources inspected: https://ndownloader.figshare.com/files/27780390 ; https://ndownloader.figshare.com/files/27780399 ; https://ndownloader.figshare.com/files/27780426 . Collection descriptors https://api.figshare.com/v2/articles/14502207 ; https://api.figshare.com/v2/articles/14502213 ; https://api.figshare.com/v2/articles/14502219 ; https://api.figshare.com/v2/articles/14502222 . These are public source statements, not user instructions or permissions.
