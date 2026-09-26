# mega27-04-microbiome-twin
Microbiome digital twin: predict community composition from species assemblage, benchmarked on the six real ecosystem datasets of the cNODE study (Michel-Mata et al. 2022, PMC9221840; data via github.com/yixueyang/cNODE).
Models on identical folds: presence-mean null, cNODE re-implementation, gLV replicator, GraphTwin (attention GNN over present taxa with learned interaction gates).
Run tests: `python -m pytest -q`. Run benchmark: `python run_bench.py Drosophila_Gut presence_mean,cnode,glv,graphtwin 10`.

## GraphTwin v2 (TwinStack) and v2b (ConstStack)
TwinStack (`graphtwin2`): per-sample convex combination of the four base predictors,
weights from a small MLP gate over assemblage summaries, trained on inner out-of-fold
predictions (no leakage; PREREG_graphtwin2.md). ConstStack (`graphtwin2b`): constant
per-dataset simplex weights + inner-OOF base-subset selection (PREREG_graphtwin2b.md).
Run: `python run_bench.py Human_Gut graphtwin2 10` (or `graphtwin2b`).
Numerical-safety: any NaN base prediction falls back to the presence-mean null's.

## Expansion in progress (not a completed platform)
Udita reopened this project for a cross-source microbiome-twin framework, an external-validation leaderboard, intervention stress tests, reliability index, multimodal/scale studies and dynamic keystone prediction. See `EXPANSION_PLAN.md` for gates and verified/thin/missing status. The existing v3 paper predates this expansion.

Initial research-use tool: `microtwin dependence paired_outer_losses.csv --group-column study` accepts a CSV with `sample_id,prior_error,interaction_error,study` measured on identical untouched outer test cases. It returns a signed fractional predictive gain per sample and group-bootstrap ecosystem median (negative means the interaction model is worse). This is **not** a causal interaction measurement or a score for an unlabeled patient: paired measured outcomes and valid held-out predictions are required. Metadata screening of the original 160 MGnify rows is in `results/expansion_manifest_screen.json`; none have yet been certified as independent external test datasets for the new leaderboard. No new benchmark win is claimed.
