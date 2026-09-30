# NASA RR-5: a measured assay discrepancy, September 30, 2026

Twenty terminal fecal mice have paired NASA processed V4 and shotgun profiles, joined through explicit assay filenames and matching RFID/sample metadata. Ten mice are ground controls and ten are flight mice; they occupy two listed cages, one per condition. This is not 20 independent flight-treatment replicates.

Blautia relative abundance has median 2.1728% in V4 and 0.10456% in shotgun. V4 is higher in all 20 pairs, including every mouse in each condition. Restricting each assay's denominator to its genus-assigned mass gives 3.0306% versus 0.12144%; the direction still holds in all 20 pairs. This supports a specific, reproducible measurement discrepancy in these NASA processed profiles. It does not establish the true abundance, a causal flight response, or that primer bias rather than taxonomy/database/pipeline differences explains it. About 21-fold is a ratio of group medians, not a median within-mouse fold change.

The initial paired screen tests 16 explicitly shared genera and gives 11 BH-adjusted q values below 0.05 under a mouse-independent model. Those q values are descriptive screening outputs only, not cage-aware population inference. Blautia's paired effect, all-pair direction and denominator sensitivity are the primary report. Median Bray-Curtis is 0.5301 when taxonomically unresolved residual bins remain separate; this includes taxonomy incompatibility and should not be read as biological community change.

V1V3 is oral-swab data. Similar mouse/timepoint labels do not make it another fecal measurement, and it was not pooled. All downloaded abundance values are now exposed exploratory data. No independent replication or untouched external validation is credited.

Prior work already reports RR-5 flight-associated Lactobacillus murinus/Dorea and host metabolite/bone findings. General 16S/shotgun discrepancies are also established. The exact RR-5 Blautia discrepancy is a candidate new dataset-specific reanalysis observation, not an established novel discovery; full prior-art assessment and independent biological replication remain open.

Sources:
- NASA study: https://osdr.nasa.gov/bio/repo/data/studies/OSD-417
- Live file registry: https://visualization.osdr.nasa.gov/biodata/api/v2/dataset/OSD-417/files/
- Original RR-5 paper: https://pubmed.ncbi.nlm.nih.gov/37080202/
- RR-5 full article: https://www.sciencedirect.com/science/article/pii/S2211124723003108
- Established assay-discrepancy background: https://pmc.ncbi.nlm.nih.gov/articles/PMC4837688/
- Integrative assay prior art: https://www.biorxiv.org/content/10.1101/2023.06.27.546795v1.full-text

Reproduce initial screen: `python scripts/nasa_rr5_assay_audit.py INPUT_DIRECTORY results/nasa_rr5_assay_20260930`, with the NASA TSVs and extracted ISA ZIP in INPUT_DIRECTORY. Output mapping and input hashes are included. The preread protocol is results/PREREG_20260930_nasa_assay_agreement.md. No raw reads, alignments or model training were performed; downloaded inputs total under 1.3 MB.
