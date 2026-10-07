# Palleja 2018 processed source: NOT ADMITTED in this attempt

Frozen admission commit a1c4560. Metadata/header-only unit, 2026-10-07. No numeric abundance table cells or models inspected. The educational practical text itself includes example abundances and published analysis descriptions; those source-family examples are now exposed, not untouched.

## Verified leads
- Primary paper links its author processed-data directory: http://arumugamlab.sund.ku.dk/SuppData/Palleja_et_al_2018_ABX/ . Live directory advertises Supplementary_data.tar.gz at 103M; HTTPS server reports 107,788,693 bytes.
- Educational mirror repository has no GitHub license field. Its data/annotated.mOTU.rel_abund.rarefied.tsv blob is 165,921 bytes, tree fcd62c35827efb73d89477af03dea4a6d8c8cf15. Header reader consumed only the first line for inspection and discarded remaining bytes without parsing values.
- Mirror has 57 sample columns. Primary Table S2 lists 57 samples/12 donors, with 12 each at named time points 0, 8, 42, 180 and nine at 4. Labels only were used; read counts/QC statistics were not used.
- Primary sample labels use _Dag, mirror _D. Even after that naming conversion and whitespace trim, eight primary IDs end in opt, absent from mirror: ERAS11_D4opt, ERAS12_D4opt, ERAS2_D4opt, ERAS4_D4opt, ERAS4_D8opt, ERAS6_D4opt, ERAS6_D8opt, ERAS7_D4opt. Do not silently strip opt, infer which library is represented, or claim byte-level primary provenance.
- Clinical predecessor referenced by Palleja reports oral meropenem 500 mg, vancomycin 500 mg and gentamicin 40 mg once/day on days 0-3, dissolved in apple juice. It says stool was collected the day before each named visit and reports an additional doxycycline course for one participant on days 26-28. Exact binding of clinical subjects/actual collection days/additional course to the taxonomic table remains unresolved. No untreated arm is established for these 12 donors.

## Bounded download outcome
Parent approved only author archive, 120-MB transfer/90-second ceiling, 250-MB local ceiling, metadata/README/license extraction and matrix headers only. Download timed out at the planned 90-second cap; gzip incomplete, list unsuccessful. Nothing extracted. Partial archive deleted. No retry, full profiles or raw reads. This is retrieval failure, not evidence the archive is absent or invalid at its source.

## Remaining admission gates
Specific data-use terms; author-table identity and opt-suffix meaning; exact collection-versus-visit timing; clinical-to-profile subject join including additional antibiotic exposure; full source-family mirror independence. NOT ADMITTED pending these gates. No causal validation, benchmark beat, discovery, reliability or replication credit.

## Observed sources
- https://www.nature.com/articles/s41564-018-0257-9
- http://arumugamlab.sund.ku.dk/SuppData/Palleja_et_al_2018_ABX/
- https://arumugamlab.sund.ku.dk/SuppData/Palleja_et_al_2018_ABX/Supplementary_data.tar.gz
- https://github.com/liampshaw/ID-microbiome-practical
- https://api.github.com/repos/liampshaw/ID-microbiome-practical
- https://api.github.com/repos/liampshaw/ID-microbiome-practical/git/trees/master?recursive=1
- https://raw.githubusercontent.com/liampshaw/ID-microbiome-practical/fcd62c35827efb73d89477af03dea4a6d8c8cf15/data/annotated.mOTU.rel_abund.rarefied.tsv
- https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41564-018-0257-9/MediaObjects/41564_2018_257_MOESM4_ESM.xlsx
- https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0142352
- https://www.nature.com/articles/s41522-019-0103-8 (same-source reanalysis, not independent replication)

## Amended retry addendum
Parent approved one 120-MB/300-second retry with ranged transfer, same extraction limits and stop-on-larger-size/unclear-rights rule. Exact 107,788,693-byte archive retrieved; command-time interruption at 97,517,568 bytes was continued using server-confirmed HTTP 206 range resume. Paths-only listing found 24 members totaling 1,083,383,045 uncompressed bytes, above the 250-MB local ceiling. Inventory has abundance/function tables but no README, license or sample-map file. Stop rule applied: no extraction or matrix header inspection, archive deleted. Aggregate path/size/hash receipt is `results/palleja_author_archive_inventory_20261007.json`. Processed data retrievability is now PASS; rights, opt-suffix identity and exact collection-day binding remain UNVERIFIED. Overall NOT ADMITTED unchanged. First timed-out transfer remains historical truth, not current download status.
