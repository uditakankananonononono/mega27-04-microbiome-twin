# External-transfer ingestion pilots, 2026-09-26

Two new study-level raw SSU tables downloaded from their exact MGnify manifest URLs, not copied from the prior 160-study audit's processed files. These are **pilot source bytes only**, not held-out model results, independently verified patient cohorts, or proof of a 500-1000-dataset leaderboard.

| MGYS | Source URL | downloaded SHA-256 | raw shape (taxa rows x sample columns) | biome | caution |
|---|---|---|---|---|---|
| MGYS00002394 | https://www.ebi.ac.uk/metagenomics/api/v1/studies/MGYS00002394/pipelines/4.1/file/SRP051741_taxonomy_abundances_SSU_v4.1.tsv | 986ec56e30f878bffc931237de13e7596ffc6beb8ea0f7f86e40e2bb0409f83d | 505 x 20 | Oral | Taxonomic hierarchy rows include mixed ranks; harmonize to genus in train-only preprocessing. Subject IDs, consent and overlap not checked. |
| MGYS00006019 | https://www.ebi.ac.uk/metagenomics/api/v1/studies/MGYS00006019/pipelines/5.0/file/SRP126632_taxonomy_abundances_SSU_v5.0.tsv | d08d75586610b280109e1f93d4774e720cc17eac35019c00c17df96125e0bef0 | 444 x 20 | Insecta | v5.0 vs oral v4.1 pipeline; cross-biome and batch confounding. Subject/sample overlap and license not checked. |

The prior audit already used these accessions, so they cannot be treated as an untouched external test if its findings influenced this design. True external validation requires independent new accessions, frozen splits and preferably separate source-family holdouts (HMP, AGP, EMP). Do not use these pilots to claim an external benchmark win.
