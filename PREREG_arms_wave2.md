# Pre-registration: wave-2 benchmark arms (locked 2026-09-25 21:31 IST, before any wave-2 fit)
Following parent ruling 21:30 IST (item 4 = one project; deeper is deeper), three more
independent baseline arms, same k=10 seed-0 protocol as the committed series:

A1. xgb: long-form XGBoost regressor (mirror of the lgbm arm): features = presence vector
    + taxon index, XGBRegressor(n_estimators=300, learning_rate=0.05, random_state=seed),
    clip at 0, mask absent taxa, renormalise; degenerate rows -> uniform over present.
A2. catb: long-form CatBoost regressor, CatBoostRegressor(iterations=300, learning_rate=0.05,
    random_seed=seed, cat_features=[taxon], verbose=0), same post-processing as A1.
A3. ridgeclr: compositional linear arm. Fit multitask Ridge (alpha=1.0, sklearn) from the
    presence vector z to the CLR of the training compositions (clr computed on present taxa
    with a 1e-6 pseudo-count over present entries only). Predict clr_hat(z), map back with
    softmax over present taxa.
Evaluation: same LOO-style k=10 cross_validate, median Bray-Curtis, paired bootstrap vs the
best v1 base per dataset. Losses are committed and reported, not hidden. These arms are
independent baselines: they do not enter the TwinStack/ConstStack blends (stack composition
stays locked at the 4 pre-registered bases).
