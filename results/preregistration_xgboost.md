# Pre-registration: does GAI add out-of-sample predictive value for ridge keystone fraction under a non-linear learner? (XGBoost; tool 33; committed before any model fitting)
Data: genera of results/keystone_kegg_genus.csv with GAI, merged with log10 mean relative abundance (results/keystone_genus_abundance.csv.gz, genus mean) and log10(1 + ENA assemblies) (results/keystone_ena_counts.csv); complete cases.
Models: XGBRegressor(n_estimators=300, max_depth=3, learning_rate=0.05, subsample=0.8, colsample_bytree=1.0, random_state=seed) predicting frac_top. Full = {GAI, lra, log_ena}; reduced = {lra, log_ena}.
Protocol: 20 repeats (seeds 0-19) of 5-fold KFold(shuffle, random_state=seed); identical splits for both models; pooled out-of-fold R^2 per repeat; delta = R^2_full - R^2_reduced.
Gate G1: >= 180 complete-case genera.
Pass (X1): mean delta > 0 AND delta > 0 in >= 15 of 20 repeats (two-sided sign-test p < 0.05).
Ridge keystone definition only.
Script: scripts/keystone_xgboost.py; output results/keystone_xgboost.json.
