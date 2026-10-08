# Validation-selected multi-model comparison engine

Software evidence only. No biological outcomes downloaded or fitted.

The earlier comparator statistic compared one submitted pair without selecting a comparator or controlling a family of tests. `microtwin.multimodel_leaderboard` adds a two-stage API:

1. `freeze_comparator` uses only disjoint validation-family median Bray-Curtis losses to choose the best non-candidate model. Equal scores use a deterministic lexical tie break. Retain the returned record before inspecting test outcomes; its timing is not authenticated by this software.
2. `compare_frozen_models` requires complete paired test errors for every frozen model and disjoint submitted validation/test family labels. Failed/missing models cannot silently disappear. It reports the frozen comparator's family bootstrap interval using the existing macro-median statistic, alongside exact two-sided family-level sign-flip tests and Holm correction across all candidate-versus-baseline comparisons.

Exact enumeration is bounded to 2-16 test families; bootstrap is bounded to 10,000 draws. The same family has one median regardless of its sample count. Independent families, symmetric/exchangeable paired differences, valid loss generation, fair information/compute, rights, taxonomy, actual biological identities and frozen timing remain separately reviewed assumptions. A source-family median is not a patient-specific guarantee. Unknown mirrored sources cannot be repaired by arbitrary labels.

Synthetic fixtures verify test-best selection cannot replace validation choice, family rather than sample weighting, exact p=2/256 for eight same-sign differences, Holm correction, tie handling, unchanged selection records, and refusal of family overlap, incomplete models, altered comparator, invalid losses or resource controls. These fixtures are not a discovery or scientific benchmark win. `external_win_certified` remains false. The primary bootstrap interval is descriptive until the existing scientific admission gates pass; supplementary sign-flip p-values do not replace it.

Measured-panel route: targeted Wastyk reuse clarification remains preferred to relabelling the negative yogurt/oats development forecast as the headline win. No email has been drafted/sent and no Wastyk outcome bytes opened. Parent owns the email decision. All eight expansion targets retain their source-grounded gates; no completion count changes in this unit.

## Executable walkthrough
The `freeze-comparator` and `compare-models` CLI commands now expose the two-stage API with bounded JSON input, exclusive selection output, unchanged-input checks and test-input hash output. A copy-ready example in `examples/multimodel/README.md` explicitly distinguishes synthetic statistics from biological evidence. End-to-end tests cover retained validation choice, refusal of modified input schema, family overlap, model dropping, malformed/oversized/symbolic inputs and preserved existing selection. Loss values must be numeric, not implicitly coerced boolean/string values. No source-family labels or row-level errors appear in the comparison stdout.

## 15:21 privacy regression correction
Inspection found that the nested legacy paired statistic still included its `study_deltas` mapping, echoing submitted family labels despite the aggregate-output promise. The new multi-model report now removes that mapping without changing numeric deltas, intervals, legacy API or archived results. An actual CLI stdout regression test checks private family tokens cannot appear at any nesting depth. No biological run or scientific claim changed.
