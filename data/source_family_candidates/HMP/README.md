# HMP V1-3 source intake, not a scored external benchmark

The public HMP16SData V13 documentation is https://waldronlab.io/HMP16SData/reference/V13.html . The package's versioned source commit used here is https://github.com/waldronlab/HMP16SData/commit/a9807c3ed97f24c94d40fc4e62329a2d83a7e673 . The three checked-in source files came from that commit's `inst/extdata`:

- `otu_table_psn_v13.txt.gz`: https://raw.githubusercontent.com/waldronlab/HMP16SData/a9807c3ed97f24c94d40fc4e62329a2d83a7e673/inst/extdata/otu_table_psn_v13.txt.gz
- `v13_map_uniquebyPSN.txt.bz2`: https://raw.githubusercontent.com/waldronlab/HMP16SData/a9807c3ed97f24c94d40fc4e62329a2d83a7e673/inst/extdata/v13_map_uniquebyPSN.txt.bz2
- `ppAll_V13_map.txt`: https://raw.githubusercontent.com/waldronlab/HMP16SData/a9807c3ed97f24c94d40fc4e62329a2d83a7e673/inst/extdata/ppAll_V13_map.txt

SHA-256 values are asserted in `scripts/hmp_v13_intake.py` and recorded in `results/hmp_v13_intake.json`. The HMP16SData package `DESCRIPTION` at the same commit lists Artistic-2.0 for the **package**; this is not a conclusion about redistribution terms for the underlying HMP participant data. The HMP public data model is described at https://www.hmpdacc.org/hmp/overview/data-model/ . No controlled clinical metadata were fetched.

Outcome-blind QC from `python scripts/hmp_v13_intake.py`: 43,140 OTUs, 2,910 matrix sample columns, 2,898 exactly joined to public metadata, 12 unmatched and excluded. The joined samples map to 179 RSID people, 18 body subsites and repeated visits; those are **one source cohort**, not 18 independent datasets. The existing 160-row MGnify manifest has no textual occurrence of `SRP002395`, `SRP002012`, `HMP`, or `Human Microbiome Project`. That is not a full sample/source mirror search.

Five genus names have conflicting higher-rank paths inside this release (Bacillus, Bacteroides, Clostridium, Eubacterium, Ruminococcus). Excluding those whole names plus unnamed genera retains median 94.77% raw OTU count mass overall but only 28.44% median among 187 stool samples; minimum across all samples is zero. Full-community genus transfer cannot be claimed from this mapping, especially for stool. The HMP V1-3 RDP/OTUPipe processing is different from EMP V4 Greengenes and from MGnify pipelines. Synonym/reference mapping, biological unit eligibility, true source independence, study-specific permissions and a frozen task-specific protocol remain open. No model fitting, test error, intervention inference, or top-tool comparison was performed.
