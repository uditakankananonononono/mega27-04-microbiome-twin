# Pre-registration: anaerobe-keystone under a third network definition (python-igraph betweenness on CLR correlation networks; tool 31; committed before any network computation)
Motivation: tool 25 (gglasso degree) failed H1, so the association looks ridge-specific. This tests a third, structurally different keystone definition (bridging position rather than interaction strength).
Method: per MGnify study, filtering and CLR correlation matrix identical to scripts/keystone_gglasso.py (filt, clr_corr). Undirected graph with an edge where |r| >= 0.3; betweenness centrality (igraph, unweighted, normalised by igraph defaults); top = betweenness >= study 90th percentile and > 0. Studies with no edges are dropped.
Test: within-study logistic model top_bc ~ GAI + log10(mean relative abundance) + prevalence + C(study), SE clustered by study (same as tools 25/KEGG).
Gate G1: >= 140 studies with a graph having >= 1 edge.
Pass (I1): GAI coefficient > 0, two-sided p < 0.05. Fail -> recorded; supports method-specificity.
Reported (not gates): Cohen's kappa vs ridge top labels; Spearman of genus-level top fraction vs ridge frac_top (genera in >= 20 studies).
Script: scripts/keystone_igraph.py (per-study cache results/keystone_igraph_per_study.csv.gz); output results/keystone_igraph.json.
