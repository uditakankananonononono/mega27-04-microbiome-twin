# Wastyk SCFA schema admission update, October 9, 2026

Decision: NOT ADMITTED for the requested forecast evaluation. Research-use clarification permits the bounded source review under the parent's decision, but units, QC/censoring, population reconciliation and compatible forecast horizon are unresolved. No model fits, predictions or evaluation effects were produced. No concentration values were printed, summarized or inspected for model decisions. Deserialization necessarily loaded the Result column into local memory; only metadata and null counts were inspected. No raw data are committed or redistributed.

## Rights and provenance
A reply in the approved request thread from the observed address jsonnenburg@stanford.edu states non-profit research use is available for repository data. The parent accepted it for academic fitting and aggregate evaluation publication as requested in the original email. It is a research-use clarification, NOT an open redistribution or commercial license. No raw redistribution or commercial claims. Mailbox authorship is UNVERIFIED: the address matches the primary-paper lead contact and references the exact request, but authentication evidence is unavailable. These facts do not certify the author's identity or rights authority. No further email was sent. The completed reply watch was removed.

## Bounded source acquisition
Pinned source commit: 37f4c511c37d368383909c2c49b85fae7040e314. Three files downloaded into private local storage, total 17,701 bytes: the 9,915-byte SCFA RDS, 545-byte diet key, and 7,241-byte demographic metadata (schema inspected, demographic values not used). RDS SHA256: 73ba46725e125056a334f3b3dfa58d2740886a9e8fc1e72ad58770ca1a451fb2. Author SCFA code and primary methods were read as documentation, not executed. No derived difference or LOOCV objects downloaded.

## Admission findings
- The RDS has 1,314 rows, 38 people, 150 specimens, columns Tube_ID, Participant, Timepoint, Group, Analyte, Result. Eight SCFAs plus lactate. No null cells or duplicate person/visit/analyte rows. Every specimen maps to one person and one visit. One specimen per stored person/visit; diet-key joins complete and agree with arm labels.
- Stored visits are 1, 2, 6, 7. Author plotting code maps these nominally to weeks -2, 0, 8, 10. There are no collection dates. Targets are not the four-week yogurt/oats task; protocol compatibility is not established.
- The original object contains 20 fiber and 18 fermented participants. Author code first excludes two labels and separately excludes two nonrandomized labels. Applying both recipes yields 34 people (16 fiber, 18 fermented), not the published final 36-person count. The primary describes dropout/antibiotic exclusions and two nonrandomized fiber participants. Internal consistency does not silently certify published-population equivalence.
- Full primary methods say approximately 20 mg stool was kept frozen, shipped on dry ice and sent to Metabolon for absolute quantitation. This supports specimen and service, not an inferred measurement unit or a GC-MS SCFA claim. The adjacent GC-MS method is for stool carbohydrates, not SCFAs.
- Neither RDS nor author SCFA code states units, LLOQ/ULOQ, censor/analysis flags or assay QC thresholds. Primary SCFA methods do not supply these. Finite/nonnegative outcomes have not been evaluated because no admitted outcome protocol exists. A linked 277.5 KB supplement PDF request returned HTML rather than PDF; that supplement was not inspected and remains unverified. An HTTP success alone was not treated as content success.

## Claims boundary and next decision
The source is already viewed development context, never untouched external validation. A new assay/diet/horizon is not automatic replication. No taxonomic twin, causal, clinical, leading-tool benchmark, reliability or discovery claim follows from these metadata. Do not fit around absent units/QC or quietly replace the endpoint. Resolving the source dictionary and randomized analysis population is needed before a task-specific frozen protocol and bounded fit plan. Author clarification is a possible next route, but requires fresh exact email review; none is drafted or sent by this update. The prior failure remains historically correct and is amended by this new rights progress plus continuing scientific-admission failure.

Sources observed:
- https://pmc.ncbi.nlm.nih.gov/articles/PMC9020749/
- https://github.com/SonnenburgLab/fiber-fermented-study/
- https://raw.githubusercontent.com/SonnenburgLab/fiber-fermented-study/37f4c511c37d368383909c2c49b85fae7040e314/data/scfa/scfa_data.rds
- https://raw.githubusercontent.com/SonnenburgLab/fiber-fermented-study/37f4c511c37d368383909c2c49b85fae7040e314/data/metadata/diet_key.csv
- https://raw.githubusercontent.com/SonnenburgLab/fiber-fermented-study/37f4c511c37d368383909c2c49b85fae7040e314/data/metadata/FeFiFo_demographics_by_participant.csv
- https://raw.githubusercontent.com/SonnenburgLab/fiber-fermented-study/37f4c511c37d368383909c2c49b85fae7040e314/R/scfa/scfa_working.Rmd
- https://pmc.ncbi.nlm.nih.gov/articles/instance/9020749/bin/NIHMS1722178-supplement-1.pdf (HTML returned, unverified)

## Afternoon supplement hunt and approved clarification
The publisher page exposed actual CDN links after its browser challenge cleared. Document S1 was retrieved as a real PDF, 246,350 bytes, SHA256 8b2d1b57949f6ccdff5f0e447e6a59bda837f7d45ae64ab7503ad4096cf5776f. All six pages text-inspected; decisive Table S2 on page 3 visually inspected. SCFA specimens are documented at weeks -2, 0, 8 and 10, 36 people per visit. This strengthens nominal schedule mapping, not actual individual intervals or RDS population identity. It confirms the lack of a four-week target rather than curing horizon compatibility.

Table S4 workbook retrieved, 15,581 bytes, SHA256 44a5b26887dedb064f4c0fad2c3abf0624de382acd3beb9187963d801b601bc9. Inspected string labels only, not reported effects or concentration means: SCFA sheet labels baseline/end as Week -2 to Week 10, without units or QC/quantification-limit fields. Reading the file into memory is not a hidden holdout; the source remains viewed development context. Document S1 contains demographics, participant-count, nutrient and protein tables, not the missing SCFA units/QC dictionary. No concentration unit inferred from other analytes or generic vendor methods.

PMC direct supplement continued returning HTML; EuropePMC supplementaryFiles returned an explicit not-open-access error rather than an archive. Those failed routes did not become successful evidence. Publisher source successfully resolved the supplement access gap, while scientific units/QC/population gates remain unresolved. Browser outcomes recorded; lease released. No fits.

User-reviewed clarification was sent once as a plain-text reply in the existing thread. Verified SENT label and exact recipient/body readback. It asks for units/wet-or-dry normalization, QC/censor limits, visit dates and the intended population. Only the approved question text was sent, no data attachments. A scoped reply watch remains active for source documentation, not a standing email auto-send grant. No further follow-up email without exact review.

Additional sources actually retrieved:
- https://www.sciencedirect.com/science/article/pii/S0092867421007546
- https://ars.els-cdn.com/content/image/1-s2.0-S0092867421007546-mmc1.pdf
- https://ars.els-cdn.com/content/image/1-s2.0-S0092867421007546-mmc2.xlsx
- https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9020749/supplementaryFiles (explicit unavailable error, not supplementary content)
