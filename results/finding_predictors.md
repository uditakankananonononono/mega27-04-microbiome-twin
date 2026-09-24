# What predicts where interaction models beat the population prior? (160 MGnify studies)
Source: results/predictors_audit.json, results/predictors_covariates.csv (scripts/predictors_audit.py).
- The OLS model (standardised covariates, HC3 robust SEs) has R^2 = 0.47. A random forest reaches 5-fold CV R^2 = 0.37.
- Strongest predictor: co-occurrence network density (|Spearman rho| > 0.3 among genera with prevalence >= 20%). Std beta 0.026, p = 0.00076. It is top in RF permutation importance. Marginal Spearman with gain is 0.61.
- Also independent: beta dispersion (Bray-Curtis, p = 0.0051), taxa count (p = 0.0061) and sample count (p = 0.034).
- Not independent after adjustment: Shannon diversity (p = 0.63), network modularity (p = 0.89), assembly-derived flag (p = 0.70), human-gut flag (p = 0.24).
  Their marginal correlations (-0.35 to -0.55) are absorbed by density, dispersion and size.
- Caveat (circularity): the interaction model learns from the same co-occurrence structure that network density summarises, so this is
  partly expected. The practical use is a pre-fit diagnostic: network density predicts whether a twin gains from interactions before one is fit.
  It is not evidence that the fitted interactions are causal.
