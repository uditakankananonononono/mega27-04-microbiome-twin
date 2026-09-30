# RR-5 paired longitudinal composition reanalysis

Twenty live-return mice have three fresh-fecal measurements and three oral measurements, matched by RFID plus material/time metadata. These are 20 mice, 120 assay samples, not 120 independent animals. One listed cage per condition limits treatment inference.

In the 10 flight live-return mice, 9 have higher fresh-fecal genus Bray-Curtis distance to their own baseline at week 9 than week 4.5. Median distances rise from 0.2021 to 0.4564. Ground controls also drift: 8/10 have greater distance, medians 0.1414 to 0.2874. Removing unassigned genus mass leaves 8/10 flight mice farther from baseline; removing dominant Parabacteroides and renormalizing leaves 9/10. This is a descriptive within-cohort result, not a causal flight effect or evidence of poor health. It is not proof of a population recovery trajectory.

Prior art materially limits novelty: the original paper already describes a community shift from week 4.5 onward and persistence to week 9, with facility/environment changes as possible explanations. Our exact paired distance-to-own-baseline numbers are a reanalysis extension, not a discovery of persistent community change. Original source: https://pmc.ncbi.nlm.nih.gov/articles/PMC10344367/ .

Oral distances do not show the same all-mouse pattern: 5/10 flight and 7/10 ground mice are farther from baseline at week 9. Oral and fecal sequencing use different regions/platforms, so cross-material differences cannot be assigned solely to biology.

Source registry: https://visualization.osdr.nasa.gov/biodata/api/v2/dataset/OSD-417/files/ ; study: https://osdr.nasa.gov/bio/repo/data/studies/OSD-417 . Mapping, individual distances and sensitivity outputs are included. No raw-read processing or model run. All values are exploratory/exposed. Reproduce with scripts/nasa_rr5_longitudinal.py INPUT_DIRECTORY OUTPUT_DIRECTORY. Sensitivity variants are denominator checks, not independent replication.
