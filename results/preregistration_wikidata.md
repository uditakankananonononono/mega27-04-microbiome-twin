# Pre-registration: Wikidata Gram-stain replication of a Madin null (tool 26; committed before any genus-level query; one count query was run to check the endpoint: 3,118 genus items carry P2597)
Data: Wikidata SPARQL endpoint (query.wikidata.org): items with taxon rank genus (P105 = Q34740) and Gram staining (P2597), with their taxon name (P225). Gram-negative = value Q632006 ("Gram-negative bacteria"), Gram-positive = Q857525 ("Gram-positive bacteria"); genera with both or other values excluded. Cached to results/keystone_wikidata_gram.csv.
Genera: results/keystone_traits.csv (ridge keystone frac_top).
Gate G1 (annotation validity): >= 80% binary agreement with Madin gram_neg (>= 0.5) on shared genera, n >= 100.
Hypothesis W0 (replication of the Madin null, rho = -0.018, q = 0.91): Spearman(frac_top, Wikidata gram_neg) has two-sided p >= 0.05. W0 is "replicated" if p >= 0.05, "contradicted" if p < 0.05.
Script: scripts/keystone_wikidata.py; output results/keystone_wikidata.json.
