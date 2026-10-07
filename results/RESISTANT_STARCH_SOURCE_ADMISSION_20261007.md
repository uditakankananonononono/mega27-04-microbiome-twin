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
