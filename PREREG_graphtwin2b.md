# Pre-registration addendum: graphtwin2b (constant-weight stack + inner-OOF base selection)

Locked 2026-09-25 15:25 IST, before any fitting of graphtwin2b. TwinStack v2
(feature-gated MLP stack) result on Drosophila_Gut: 0.0868 vs glv 0.052 -
point loss, paired-bootstrap CI of the difference spans zero (-0.006, 0.062).
Per the v2 pre-reg falsification clause, the direction pivots within the project.

## Diagnosis (from committed results only)
The MLP gate (19 inputs, 16 hidden, ~400 parameters) overfits inner OOF noise
on small datasets (Drosophila n=24). The blend never reaches the glv vertex.

## graphtwin2b changes (both locked now)
1. Gate = constant per-dataset simplex weights w (4 free logits, no assemblage
   features), trained on the same inner OOF predictions, 400 epochs, lr 0.05,
   full-batch L-BFGS-free Adam. The simplex includes every base-model vertex,
   so training can in principle reach the best single model.
2. Base-subset selection: per outer fold, the inner OOF median BC of each base
   is computed; bases whose inner-OOF median exceeds the best base's by more
   than 0.05 are dropped from the stack (min 2 bases kept, always including
   the inner-OOF best and presence_mean as the safety floor). Selection uses
   ONLY inner-train information; outer-test folds never influence it.

## Win criterion (unchanged from v2 pre-reg)
graphtwin2b out-of-fold median BC <= best single baseline's median on every
one of the six cNODE datasets, same folds, same seed (k=10, seed 0); paired
bootstrap CIs reported; CI lower bound > 0 = honest loss, reported as such.
v2 numbers remain in the repo and the paper as the record of the first attempt.
