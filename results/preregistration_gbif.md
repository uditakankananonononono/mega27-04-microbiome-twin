# Pre-registration: habitat/geographic generalism rival (GBIF API; tool 28; committed before genus queries; one connectivity check on "Eikenella" match and one facet query on an unrelated key)
Data: GBIF API v1 species/match (name=<genus>, rank=GENUS, kingdom=Bacteria; accept matchType EXACT and rank GENUS and kingdom Bacteria or Archaea) -> usageKey; occurrence/search?taxonKey=<key>&limit=0&facet=country&facetLimit=300 -> total occurrences and number of countries. Cached to results/keystone_gbif_counts.csv.
Rival G: ridge keystones are cosmopolitan generalists; anaerobe status (GAI) proxies for generalism.
Model: OLS frac_top ~ GAI + log10(1 + occurrences) + log10(1 + countries) + log10(mean relative abundance), HC3, genera in results/keystone_kegg_genus.csv with GAI and a GBIF match with >= 1 occurrence.
Gate G1: >= 150 genera in the model.
Pass (B1): GAI slope > 0 with two-sided p < 0.05. Rival G is supported only if a generalism term is significant (p < 0.05, positive) AND GAI loses significance.
Script: scripts/keystone_gbif.py; output results/keystone_gbif.json.
