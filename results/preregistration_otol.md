# Pre-registration: does the anaerobe-keystone PGLS result survive an independent phylogeny? (Open Tree of Life; committed before any OToL tree download)
Data: Open Tree of Life API v3 (api.opentreeoflife.org): TNRS match_names (context Bacteria, exact matching, genus rank only) for genera in results/keystone_kegg_genus.csv with a non-missing GAI; induced synthetic subtree (tree_of_life/induced_subtree, label_format id) over the matched OTT ids.
The OToL synthesis tree has no branch lengths; we assign Grafen (1989) lengths (node height = number of descendant tips - 1, scaled to root height 1). Brownian covariance V_ij = shared root-to-LCA height; Pagel lambda by ML on the grid 0..1 step 0.05.
Model: GLS frac_top ~ GAI.
Gate G1: >= 150 genera matched and present as tips in the induced subtree.
Pass criterion (H1): GAI slope > 0 with two-sided p < 0.05 under full Brownian motion (lambda = 1). Secondary (reported, not a gate): p at lambda_ML; Pagel lambda of frac_top alone with LR test vs 0.
H1 fails if the Brownian p >= 0.05; that result will be recorded as a failure of phylogenetic robustness on this tree.
Script: scripts/keystone_otol.py; output results/keystone_otol.json.
