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
