# Two-stage comparison walkthrough (synthetic only)

From an installed local checkout, run:

```
microtwin freeze-comparator examples/multimodel/validation.json --candidate twin --out /tmp/microtwin-selection-new.json
microtwin compare-models examples/multimodel/test.json --selection /tmp/microtwin-selection-new.json --n-boot 100
```

Choose a new selection output path each time. The validation winner is `prior` and stays selected even though `cnode` has lower test error than `twin`. This exposes why beating one validation-selected comparator is different from dominating the whole leaderboard. These invented losses verify software mechanics only. Two families give a very coarse randomization test; do not infer a biological win from the negative bootstrap interval on these constant toy differences.

Inputs have exactly `errors` (model names to equal-length arrays of Bray-Curtis losses) and `families` (one submitted source-family label per paired row). Model failures must not be omitted. Use the same sample order for every model. At most 20 models, 10,000 rows, 1 MB per input and 2-16 test families are accepted. No model fitting or networking occurs. Timing and source/subject/assay/rights/budget authenticity require separate evidence review. Save selection before reading test outcomes; editing both the record and inputs defeats this local guard. Output includes input hashes but not family labels or sample-level errors.
