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

The requested Twin Reliability Index is currently an **unavailable composite**. `microtwin.reliability.reliability_report` records the five separate evidence components (accuracy, predictive interaction gain, uncertainty calibration, transferability, robustness), and refuses to emit an arbitrary 0-100 value. Calibration on disjoint sources plus independent domain validation must precede a numerical index. The research-use input schema likewise does not provide access control or a deployed patient-upload site.

Scale is also gated: `microtwin.scale_gate.scale_status` counts only accessions with explicit independence, license, QC, source-hash and sample-count verification. As of this expansion, the new leaderboard has **0 fully verified external datasets**, not 500-1000; no foundation-model pretraining or millions-of-samples result exists. The TransformerTwin code is an experimental, unbenchmarked baseline, not a foundation model.

## Local research intake (schema only)

`microtwin inspect abundances.tsv --unit counts --source-id study-label --processing-authorized --subject-map subjects.csv` checks a researcher-supplied samples-by-taxa TSV/CSV with `sample_id` first, nonnegative finite abundances, unique IDs, counts/relative-unit consistency and exact optional CSV `sample_id,subject_id` grouping. It returns only an aggregate QC report and source checksums; input stays local. `--processing-authorized` is the researcher's declaration, not proof that the user has consent or data-use rights; those must be checked separately. It never trains or fits a patient model, forecasts outcomes, uploads data, authenticates users, or provides access control. A missing subject map cannot support grouped split. File size is limited to 50 MB for this local intake command. **This is not the requested deployed digital-twin platform.**

External validation update: the first EMP multi-study debug pilot failed its vocabulary gate and used ambiguously mapped genus strings (`results/pilot_emp_transfer_README.md` and EMP source README). The HMP V1-3 candidate is now also a viewed, input-only development diagnostic; all 18 body subsites fail the prospective minimum-sample 90%-raw-count-mass gate for old oral vocabulary (`results/hmp_v13_input_coverage.json`). Neither supports a top-tool win or full-community transfer claim. No calibrated TRI or validated intervention forecast exists.

A synthetic-tested longitudinal study-design preflight (`microtwin.perturbation_design.screen_paired_design`) checks whether metadata have paired pre/post subjects by treatment arm and phase. It does not access outcomes or make causal claims. Research program remains open after negative diagnostic tests: no external benchmark win, replicated discovery, calibrated reliability composite or 50+ text-body-page expanded paper is yet available. ChatGPT judge rounds for this expansion: 0/10 at the 16:12 checkpoint.
