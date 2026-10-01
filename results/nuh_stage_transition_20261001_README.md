# NUH stage-transition diagnostic

This is a non-causal development test using author-labelled PRE and DURING stages. Drug, dose, Case/Control exposure semantics and whether day-1 PRE is truly pre-treatment remain unknown after accessible main/supplement, browser preview and all ENA sample-attribute inspection. It is not an antibiotic-response validation.

Twenty-four subject labels (13 Case, 11 Control) each supply one PRE/DURING pair; 255 species-terminal features are retained without double-counting parent/strain rows. Same-group leave-one-subject-out median-change prior gives 62.43% subject-macro accuracy with 54.38% eligible-change coverage; fixed three-neighbor prior gives 58.64% at 61.44%. The difference is -3.79 percentage points, subject-bootstrap 95% interval -9.92 to +2.24 points. Neither is an interaction model or a novel method. These coverage-conditional scores are not a fair matched-coverage leaderboard comparison.

Post-primary common-scored-taxa sensitivity gives difference -2.22 points, interval -7.45 to +2.95 points; no supported nearest-neighbor gain. This is explicitly secondary and was added after viewing primary results. Subject-label bootstrap is not proof of independent biological units.

Input abundance SHA-256 and aggregate results are in the JSON. Participant metadata and clinical tables are not published in this repository. Re-fetch the pinned source to run scripts/nuh_stage_transition.py. No POST/recovery-status outcome labels were used. Tables are exposed development data, not untouched final validation. No top-tool beat, new biology or perturbation-validation gate is credited.

Sources:
- https://github.com/CSB5/Recovery_Determinants_Study
- https://raw.githubusercontent.com/CSB5/Recovery_Determinants_Study/d374f5e7c09da659d407af5664604b81451c5df4/Data/NUH_StoolSamples_MetaPhlAn2.txt
- https://raw.githubusercontent.com/CSB5/Recovery_Determinants_Study/d374f5e7c09da659d407af5664604b81451c5df4/Data/Metadata.xlsx
- https://www.ebi.ac.uk/ena/browser/api/xml/PRJEB41865
- https://www.nature.com/articles/s41559-020-1236-0

Causal antibiotic-direction question remains parked until original course/arm timing is supplied by a retrievable source. Mouse SRP142225/PRJNA450709 source has published cage units and gavage groups, but dosing schedule/profiles still need their own frozen protocol.
