# Pre-registration: is anaerobe-keystone explained by genome streamlining? (committed before any NCBI Datasets download)
Data: NCBI Datasets v2 API, genome dataset_report per genus (reference genomes, up to 20), median total sequence length (Mb) and median GC%.
Rival hypothesis R: keystone fraction tracks small genome size / low GC, and anaerobe status only proxies for that.
Test: OLS frac_top ~ anaerobe(KEGG GAI) + log10 genome size + GC (+ log abundance), HC3 SEs, over results/keystone_kegg_genus.csv genera with genome data.
Anaerobe association PASSES if the GAI slope stays positive with p < 0.05 after adjustment. R is supported if genome size slope is significant and GAI slope loses significance.
