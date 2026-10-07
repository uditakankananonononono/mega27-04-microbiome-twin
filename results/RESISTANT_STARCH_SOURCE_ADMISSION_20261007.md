# Resistant-starch source admission, 7 October 2026

## Decision
Baxter 2019 is a promising **development source**, but is not admitted for fitting. Venkataraman 2016 is not admitted for a paired metabolite forecast. No outcome table, numeric SCFA value, participant identifier, raw read or fitted result is saved by this unit. Published effects were read during discovery. XML metadata necessarily contained values internally, although the extraction discarded them. Neither source can be described as an untouched test set.

## Rights and design
The official ENA/INSDC policy permits free, unrestricted access and analysis/publication of database records, with appropriate credit to original submissions. This covers the public deposit, not a blanket license for unrelated author files. ENA additionally notes potential benefit-sharing obligations for commercial users; this free research unit makes no commercial clearance claim.

Baxter's publication reports 174 young participants in four academic semesters from fall 2015 through spring 2017, parallel supplement groups, three or four baseline stools and three or four full-dose stools in week three. A 4-7 day transition has no stool sampling. HPLC concentrations are in mmol/kg wet feces and normalized to individual sample weight. Repeated stools are not independent participants. Dose, diet and horizon differ from the earlier yogurt experiment. This is three principal SCFAs and a total, not eight independent chemical outcomes or a direct yogurt replication.

Venkataraman reports 20 participants with four baseline and four intervention stools, three-day escalation and seven full-dose days. The assay uses the average fecal sample weight of 0.67 g for normalization. That calibration is not silently interchangeable with Baxter's individual weights.

## Live metadata evidence
SRP128128 maps to PRJNA428736: 1,205 runs and 1,201 distinct samples. Run counts do not establish the participant count. The first, middle and last sorted sample accessions all have subject, collection date, semester, supplement and before/during status attributes, plus acetate, propionate, butyrate and total SCFA attributes. Their inspected non-outcome labels span fall15, fall16 and wint17, with inulin, potato and himaize represented. This is a three-sample structural spotcheck, not complete coverage, valid units for every cell, an arm balance audit, or a subject join.

SRP067761 maps to PRJNA306884: 157 distinct samples/runs. The first, middle and last sample schemas have no explicit subject, supplement, before/during or SCFA attributes. Their collection years are 2015. Sample titles may encode information, but no decoding is attempted here.

Both studies share the University of Michigan BIO173 recruitment setting and HUM00094242 ethics identifier. The earlier study's 2015 specimens and the later cohort's fall15 specimens mean calendar years alone do not rule out overlap. Distinct publication and accession IDs are not independent recruitment evidence. Treat both as one source family until a non-outcome lineage audit establishes otherwise.

## Next gate
A complete metadata census must check stable subject keys, unique sample/run mapping, sample-specific phase/arm consistency, collection dates, missing outcome presence (not values), duplicates, and unit declarations before freezing a separate forecast protocol. No raw-read reprocessing or model training is authorized by this admission record. A year/semester-held-out design would remain same-source temporal evaluation, not independent laboratory validation. All participant rows remain unredistributed; publish only source citations, aggregate admission counts and code.

## Sources inspected
- Primary Baxter publication: https://journals.asm.org/doi/10.1128/mbio.02566-18
- Primary Venkataraman publication and license: https://pmc.ncbi.nlm.nih.gov/articles/PMC4928258/
- ENA/INSDC policies: https://www.ebi.ac.uk/ena/browser/about/policies
- Public availability status policy: https://ena-docs.readthedocs.io/en/latest/submit/general-guide/data-availability-policy.html
- Baxter accession mapping: https://www.ebi.ac.uk/ena/browser/api/xml/SRP128128
- Baxter sampled metadata: https://www.ebi.ac.uk/ena/browser/api/xml/SAMN08297754 ; https://www.ebi.ac.uk/ena/browser/api/xml/SAMN08298421 ; https://www.ebi.ac.uk/ena/browser/api/xml/SAMN08299129
- Venkataraman sampled metadata: https://www.ebi.ac.uk/ena/browser/api/xml/SAMN04370085 ; https://www.ebi.ac.uk/ena/browser/api/xml/SAMN04370163 ; https://www.ebi.ac.uk/ena/browser/api/xml/SAMN04370241

The associated JSON contains only schema names and selected non-outcome labels. Useful predictive win: not evaluated. Source admission: pending full census. Independent validation: false.

## Approved census attempt: blocked by wrong export record type
The single bounded request to the project XML browser endpoint with a dataType=SAMPLE parameter returned a 1,968-byte project record in 0.577 seconds, not linked SAMPLE elements. This is an endpoint-selection error. No retry or alternate request was made. Zero sample elements cannot be interpreted as an empty cohort or absence of metadata; the earlier accession inventory still contains 1,201 samples. Full metadata admission remains pending. The census result intentionally omits false zero-valued cohort metrics. Need verified export mechanics and a separately authorized request before another attempt.

## Corrected census: metadata complete, admission still pending
A separately approved request to the documented advanced-search endpoint returned 6,123,886 bytes in 37.854 seconds. The SAMPLE-element and unique-accession assertions both reconcile exactly to the prior 1,201-sample inventory; no duplicate sample accessions. The export contains 175 subject keys, 601 before samples and 600 during samples. Every subject has at least one specimen in both phases, but only 143 subject keys have at least three specimens in both phases. All required metadata fields are nonempty, and no subject key spans multiple arms or semesters. There are four arm labels (himaize 312, accessible 250, inulin 367, potato 272 samples) and four semester labels (wint17 509, fall16 254, wint16 153, fall15 285 samples). These are specimen counts, not arm participant counts.

All four SCFA attributes are present in all samples; finite numeric parseability counts differ: acetate 1,188, propionate 1,058, butyrate 1,167 and total SCFA 1,030. Presence is not a complete usable measured panel. No numeric outcome values were retained or analyzed, and this audit does not decide whether missing/non-numeric values mean missing assays, censoring, exclusion, or a special sentinel code. The raw XML was held in process memory only and discarded. Only aggregate census results are saved.

The publication's 174 participants and minimum-three-specimens per phase inclusion statement do not match a literal 175-key/143-eligible schema census. This discrepancy is a gate failure to resolve, not permission to discard one participant or change inclusion rules. The metadata keys may have semantics requiring further evidence; no explanation is established. The cohort is not admitted for training, held-out evaluation or biological discovery. A separate non-outcome eligibility/unit audit is needed before a scientific protocol. Neither this census nor the earlier accession inventory establishes independent recruitment or new perturbation performance.

Corrected export source: https://www.ebi.ac.uk/ena/browser/api/xml/search?result=sample&query=study_accession%3D%22PRJNA428736%22&limit=0

## Reliability checks
The census utility was refactored after the observed export into an import-safe function plus explicit command-line entrypoint. No request is made by importing the module. Synthetic fixtures test that raw subject IDs and numeric chemical values never enter output, non-finite/sentinel values are not counted as finite observations, wrong PROJECT records cannot become zero-valued cohort summaries, and duplicate sample accessions fail reconciliation. This refactor was tested offline; the real endpoint was not called again. Four new tests pass. Full suite: 451 passed, one skipped, one existing LightGBM categorical-feature warning. This is software-check evidence, not cohort eligibility validation or scientific replication.
