# External source planning ledger, 2026-09-26

This is a source-discovery ledger, not a downloaded benchmark or a license conclusion. Source-family holdout, taxonomy, consent, subject identifiers, raw-vs-processed datasets and task comparability must be verified before any model result.

| source | authoritative discovery URL | candidate data route | unresolved gate |
|---|---|---|---|
| MGnify | https://www.ebi.ac.uk/metagenomics/api/v1/studies | New accession candidates MGYS00005779 and MGYS00002146 pinned in `data/external_candidate/`; two previously audited ingestion pilots also pinned | The new soil candidate had derived assembly analyses alongside runs; the new oral candidate has repeated runs and unclear subject units. Other MGnify holdouts must remain untouched and accession-disjoint. |
| HMP / iHMP | https://portal.hmpdacc.org/ ; https://www.hmpdacc.org/HM16STR/all/index.php | Official portal 16S datasets, subject and body-site metadata | Verify exact frozen release, subject split, overlap with MGnify, taxonomic compatibility and permitted use. |
| American Gut Project | https://github.com/knightlab-analyses/american-gut-analyses | Project README identifies fixed manuscript dataset and living Qiita study 10317, EBI PRJEB11419, redbiom | Choose fixed vs living release, citation/license, disjoint subjects and abundance table; do not count parallel routes as separate datasets. |
| Earth Microbiome Project | https://earthmicrobiome.org/data-and-code/ | Project page points to Zenodo Nature archive, FTP observation/metadata and Qiita EMP portal | Choose frozen table and sample ontology, verify source study grouping and compatibility; the same samples can appear in multiple mirrors. |

MDSINE2 official model source https://github.com/gerberlab/MDSINE2 (GPL-3.0 per its repo page). cNODE original source/data https://github.com/yixueyang/cNODE . A single leaderboard across incompatible steady-state and longitudinal tasks is prohibited by the expansion gate plan.
