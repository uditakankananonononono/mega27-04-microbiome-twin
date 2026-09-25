# Pre-registration: literature-volume control with an independent index (Crossref REST API; tool 30; committed before genus queries; one connectivity check on "Eikenella" and "Cardiobacterium")
Replaces the OpenAlex design (results/preregistration_openalex.md, not run: HTTP 429). Same hypotheses, different index.
Data: Crossref API works?rows=0&query.bibliographic=<genus> -> message.total-results per genus for the 248 genera of results/keystone_disbiome_genus.csv. Cached to results/keystone_crossref_counts.csv. Note: query.bibliographic is a relevance search over titles/authors/venues, so counts are a noisy proxy of literature volume.
C1 (replication of Europe PMC E1 with a different index): NB (ML alpha) Disbiome n_exp ~ kscore + log(studies modelled) + log(1 + Crossref works); pass if kscore coef > 0, two-sided p < 0.05.
C2: same covariate added to the BugSigDB model (bugsigdb_signatures from results/keystone_bugsigdb.csv); pass if kscore coef > 0, two-sided p < 0.05.
Gate G1: >= 240 genera with a count.
Script: scripts/keystone_crossref.py; output results/keystone_crossref.json (keys O1_/O2_ correspond to C1/C2).
Tests the ridge keystone definition only (gglasso negative, tool 25).
