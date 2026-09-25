# Pre-registration: Bayesian hierarchical re-fit of the method-general oral effect (bambi/PyMC; tool 37; committed before any fitting)
Data and rows: exactly those of scripts/keystone_methodgeneral.py for gglasso and igraph labels (fit() row construction).
Model: bambi logistic top ~ oral + GAI + lra + prevalence + (1|study); default bambi priors; NUTS 2 chains x 500 draws after 500 tune, random_seed 0.
Pass (BY1): posterior P(oral coef > 0) >= 0.975 under BOTH gglasso and igraph. Reported: posterior mean and 95% HDI of oral and GAI; max R-hat (convergence flag if > 1.05).
Script: scripts/keystone_bambi.py; output results/keystone_bambi.json.
