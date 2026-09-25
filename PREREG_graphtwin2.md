# Pre-registration: GraphTwin v2 (assemblage-conditioned convex stacking)

Locked 2026-09-25 13:55 IST, before any fitting of the new model.

## Motivation
Scoreboard on identical folds (median Bray-Curtis error, lower is better;
committed results/bench_*_k10.json):
- Drosophila_Gut: glv 0.052 best; graphtwin 0.093 (2nd of 4)
- Human_Gut: presence_mean 0.256 best; graphtwin 0.287 (3rd of 4, worse than published cNODE 0.242)
- Human_Oral: graphtwin 0.202 best (1st of 4)
- Soil_Vitro: glv 0.117 best; graphtwin 0.140 (2nd of 4)
No single model dominates; each baseline wins somewhere. GraphTwin v1 is best on 1/4.

## Model: TwinStack (graphtwin2)
A per-sample convex combination of the four base predictors
(presence_mean, cnode, glv, graphtwin):
    p(x) = sum_m w_m(z) * p_m(x),  w(z) = softmax(MLP(phi(z)))
where phi(z) = [richness, richness/n, presence-weighted log-prior entropy, mean taxon embedding],
MLP = 1 hidden layer of 16 units. Weights are a 4-simplex per sample, so the
stack can reproduce any single base model and any mixture; predictions stay on
the simplex and respect absence masking because every base does.

## Stacking protocol (no leakage)
Within each outer fold: 5 inner folds on the outer-train split produce
out-of-fold base predictions for every outer-train sample; the gate is trained
on those (Bray-Curtis loss, Adam lr 0.01, 200 epochs, wd 1e-4). Base models are
then refit on the full outer-train split with the same hyperparameters as v1
(EPOCHS cnode 200, glv 200, graphtwin 150; identical seeds) and the frozen gate
combines their outer-test predictions.

## Win criterion (locked)
TwinStack is "best across all benchmarks" iff its out-of-fold median
Bray-Curtis error is <= the best single baseline's median on every one of the
six cNODE datasets (Drosophila_Gut, Human_Gut, Human_Oral, Ocean, Soil_Vitro,
Soil_Vivo), same folds, same seed (k=10, seed 0). Paired bootstrap CIs of
median(TwinStack) - median(best baseline) reported per dataset; a dataset where
the CI lower bound > 0 is an honest loss and is reported as such. No
hyperparameter of the gate is tuned on outer-test folds.
Secondary criterion: TwinStack <= published cNODE medians wherever the
re-implementation already meets them.

## Falsification / negatives
If the gate collapses to a single weight (w_m ~ 1) on a dataset, that is
reported as "no stacking gain on <dataset>", not hidden. If TwinStack loses on
any dataset, the loss is reported and the direction pivots (e.g. constant
per-dataset weights) within the project, per program rule.
