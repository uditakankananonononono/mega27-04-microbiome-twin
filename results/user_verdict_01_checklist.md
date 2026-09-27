# Research-twin benchmark reporting checklist (unvalidated proposal)

This checklist is a deliverable prompted by Udita's 2026-09-27 verdict. It does not certify the archived study or establish a new scientific result.

1. Name the task and experimental unit: within-study assemblage-to-composition, longitudinal absolute abundance, or measured intervention direction. Never pool their metrics into one leaderboard.
2. Record source family, accession, sample/subject/household/timepoint map, assay and taxonomy versions, rights and access restrictions, source byte hashes, duplicate tests, and any source mirror.
3. Freeze study-/subject-disjoint train, tuning, and untouched test partitions. Fit taxa vocabulary, imputation and normalization on training data only. Record every excluded table and why.
4. Always run a training-only population prior with the same input information and splits as interaction-aware contenders. Call a training-mean interpolator a baseline, not a personalized digital twin.
5. Use separate endpoints for detection and conditional abundance, plus an all-timepoint result when compatible; write down the scoring unit (mouse versus taxon pair) and multiplicity plan before outcomes are inspected.
6. For cross-study claims, macro-aggregate by independent source family, with source-aware intervals and a frozen comparison against the strongest eligible same-task model; negative and incompatible sources remain in the ledger.
7. For an intervention forecast, specify intervention schedule, baseline, effect threshold, direction, no-change controls, and prospective outcomes from an independent experiment. Observational network edges are not such outcomes.
8. Report parameter count, training budget, compute, failure rate and output validity, then plot paired error against capacity on compatible data; no larger-model inference from one contrast.
9. Treat inferred network hubs as method-dependent. Compare ridge, graphical lasso and betweenness on aligned units, and report top-label kappa. A genuine biological keystone needs a perturbation response, not just graph rank.
10. Archive analysis decisions before tests, distinguish preplanned from post-failure redirection, preserve falsified predictions, and state explicitly whether an external source, discovery, reliability calibration and clinical claim were actually validated.

The present audit only satisfies parts of this list. In particular, 160 MGnify tables are heterogeneous previously viewed within-study results, while the expanded platform's untouched external transfer and intervention outcomes are missing.
