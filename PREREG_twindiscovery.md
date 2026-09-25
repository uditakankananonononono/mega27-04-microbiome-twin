# Pre-registration: twin-driven discovery arm (M4)

Locked 2026-09-25 15:55 IST, before any GraphTwin-gate analysis. Builds only on
committed artefacts: the sulfate-reducer keystone enrichment (NCBI q=0.019,
GTDB q=0.020, both resting on 3 genera and flagged fragile) and the 160-study
MGnify interaction audit.

## Claim under test (two tests, both locked)
T1. Model-class independence of the keystone enrichment. Train GraphTwin
(d=32, 2 layers, 150 epochs, lr 0.005, seed 0 - the locked v1 recipe) on each
MGnify amplicon study already used by the ridge audit where >= 30 samples and
>= 20 genera survive the audit caps, plus the cNODE Human_Gut table. Score
each genus by gate out-strength: mean over present-as-source pairs of
sigma(e_i^T U e_j) (the learned edge gate), computed on the trained full-study
model. Test: one-sided Fisher enrichment of Desulfobacterota
(GTDB v232 mapping from results/keystone_gtdb.csv) among genera in the top
decile of studies by out-strength frequency (same "top in study" binomial
construction as keystone_mgnify.py, so the only change is the scorer).
Success: BH q < 0.05. Any other phylum passing is reported; nothing is hidden.

T2. Twin gates vs ridge as a disease-literature predictor. Same negative-
binomial GLM as the BugSigDB cross-check (n_signatures ~ score +
log(studies modelled)), score = twin-gate out-strength frequency. Locked
comparison: twin-gate coefficient vs ridge coefficient on the same genera and
studies; twin wins if its coefficient is positive with p < 0.05 AND the model
AIC beats the ridge-score model's. A null or a loss is reported as a negative.

## Why this is twin-driven
The keystone enrichment currently rests on a ridge linear model. If the same
3-genus signal emerges from a nonlinear attention model trained with no
knowledge of the ridge result, the "hydrogen/sulfur cross-feeding hub"
hypothesis survives a model-class change; if it vanishes, that is itself the
finding (enrichment is a linear-model artefact) and is reported as such.

## Falsification / negatives
T1 q >= 0.05 -> reported as non-replication. T2 AIC or significance miss ->
reported. Small-n fragility (3 genera) is restated in any framing.

## Redirect clauses (per user steering 2026-09-25 19:10 IST: no negative closes
while an untried method exists)
- If T1 returns null (q >= 0.05): the scorer redirects to SHAP-attribution
  centrality from the validated LightGBM keystone model (scripts/keystone_shap.py,
  SH1 PASS), same Fisher/binomial construction, locked here before any T1 run.
- If T2 loses on AIC or significance: the predictor redirects to CatBoost +
  SHAP per-genus attribution ranking (scripts/keystone_boosters.py, B1 PASS),
  same NB-GLM comparison, locked here before any T2 run.
- A negative at any step is reported in the ledger AND the redirect runs; the
  project does not close on a negative.
