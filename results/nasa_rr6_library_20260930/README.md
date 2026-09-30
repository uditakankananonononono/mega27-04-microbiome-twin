# RR-6 supports a cross-mission assay discrepancy

Blautia is higher in the NASA processed 16S FluidAA table than either matched NxtaFlex or Swift1S shotgun table in 43 of 48 paired fecal samples. Medians are 0.5560% by 16S versus 0.02716% / 0.03099% by shotgun. After restricting denominators to genus-assigned mass, medians are 0.77257% versus 0.05579% / 0.05635%, with 44/48 pairs in the same direction. RR-5 independently showed V4 above shotgun in 20/20 terminal pairs. These are measurements from two missions, not two proven comparable biological experiments. Different amplicon regions, taxonomic databases and pipelines prohibit attribution of the discrepancy to a single cause. Independent mouse identity and source overlap remain incompletely audited, so no biological replication gate closes.

Within RR-6, NxtaFlex and Swift1S shotgun profiles have median Bray-Curtis distance 0.02332 after renormalizing assigned genus mass. Swift1S has lower UNKNOWN percentage in 43/48 matched samples; median paired difference is -3.4513 percentage points. Median UNKNOWN fractions are 37.1550% and 34.5531%. This supports relative library-preparation agreement after assignment, not better absolute quantification or an improved biological predictor.

Exact sample and extract IDs match across shotgun library preparations, and 48 source/sample labels are distinct. However the field labeled ALSDA Biospecimen Subject ID has only six cohort-level values. Alternate ALSDA source identifier 3E6E repeats in ISS-T GC 6 and GC 7. Until resolved, the defensible count is 48 matched samples, not a certified 48 independent mice. No inferential p values are reported.

The original RR-6 paper reports extensive species/host changes and specific Blautia species with different directions. Its biology is prior art. The exact processed-profile assay discrepancy is a candidate dataset-specific reanalysis finding, not established novelty. General amplicon versus shotgun bias is already known. No new method or causal flight effect is claimed.

Sources:
- https://osdr.nasa.gov/bio/repo/data/studies/OSD-249
- https://visualization.osdr.nasa.gov/biodata/api/v2/dataset/OSD-249/files/
- https://www.nature.com/articles/s41522-024-00545-1
- https://pmc.ncbi.nlm.nih.gov/articles/PMC4837688/

Reproduce: `python scripts/nasa_rr6_library_audit.py data/nasa_rr6_processed results/nasa_rr6_library_20260930`. The matched mappings, per-sample outputs and source hashes are included. All processed values are exposed exploratory data, not untouched holdouts. No raw-read downloads, alignments or model training.

UNKNOWN is a MetaPhlAn estimated uncharacterized fraction, not a directly observed percentage of all unmapped reads. The marker-only read count must not be interpreted as the full community assigned fraction. Terminology reference: https://forum.biobakery.org/t/how-is-unknown-calculated/558 . Broader library-preparation comparison prior art: https://pmc.ncbi.nlm.nih.gov/articles/PMC8510527/ .
