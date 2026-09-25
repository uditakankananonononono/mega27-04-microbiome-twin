# Pre-registration: benchmark arms cNODE2 and LightGBM-composition

Locked 2026-09-25 19:50 IST, before fitting either arm. Per user steering
7:42/7:49 PM: our pipeline must be benchmarked against the strongest existing
tools for its job on fair comparisons.

## Arm A: cnode2 (Michel-Mata 2022's stronger variant)
Two stacked cNODE1 layers trained end-to-end on Bray-Curtis loss:
x1 = cNODE1(z; W1), p = cNODE1(x1; W2). Same integrator, steps=20, epochs=200,
lr=0.01, wd=1e-4, batch=32, seed=0 - identical to the cNODE arm so the only
change is depth. Same folds as all committed benchmarks (k=10, seed 0).

## Arm B: lgbm (strongest off-the-shelf ML tool)
Long-form supervised model: rows = (sample, taxon); features = presence vector
(n bits) + taxon id (categorical); target = relative abundance. LightGBM
regression, default depth, lr 0.05, 300 boosting rounds, early stopping off,
seed 0. Prediction masked to present taxa and renormalized to the simplex.
Same folds (k=10, seed 0).

## Role in the comparison
Both arms enter the per-dataset baseline table as independent baselines. They
do NOT enter the TwinStack/ConstStack stacks (the locked stack protocol names
its four bases; changing stack composition post-lock would break comparability
with the committed v2/2b runs). Win criterion for our pipeline is unchanged:
<= best baseline on all six datasets, where "best baseline" now ranges over
presence_mean, cnode, cnode2, glv, graphtwin, lgbm.
