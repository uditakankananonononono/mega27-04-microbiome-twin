# Gurry2021 ex vivo admission: measured perturbation, unresolved units and replicate provenance

Role is descriptive/development only; published effects were viewed. This is an ex vivo donor-stool perturbation source, not an in-vivo clinical diet forecast, personalized absorption model, independent discovery or untouched validation. The in-vivo panel hunt remains open. One46,217byteCCBY4.0workbook was downloaded; only text schema and sample-ID metadata were parsed. No numeric chemical cells were read, summarized, fitted or retained in output. Chip sheet excluded.

Primary methods document MITCOUHES1510271631, stool diluted1g/5mL, control/inulin/pectin/cellulose conditions,0/2/4h and GC-FID. Workbook explicitly declares concentrations as mM and empty cells as no acid detected. The latter is a detection-limit flag, not permission to impute zero. The primary wording also describes mM concentrations per gram raw sample and per mL slurry. Without clarification, the normalization cannot be silently collapsed into mmol/kg stool or multiplied by five. Rate plots use mM/h. No numerical biological interpretation is made in this admission pass.

Subset1 has142uniqueIDrows and5donorlabels. The frozen two-suffix parser initially accepted118and failed24; all24failures are suffix c at2/4h, across3of the existing5labels. They are retained, not discarded. Revised metadata-only parsing accounts for all142: Ctrl36,Cell36,Inul35,Pect35; timecodes00:38,02:52,04:52; suffixa60,b58,c24. The third suffix conflicts with the primary statement of two wells per timepoint. Its biological/technical role is unresolved. It supplies no additional independent donor.

Subset2 has666uniqueIDrows and37donorlabels, all parsed under its separate code convention00/01/02=0/2/4h. Ctrl222,Cell148,Inul148,Pect148rows; suffixa333,b333. Control has baseline0h; intervention conditions have2/4h only. A per-condition0h baseline cannot be invented. Donor labels do not overlap between sheets, giving42distinctlabels, but42independently recruited people is not verified by that arithmetic. Sheet counts and labels are not independent studies.

Admission: explicit rights, small transfer and clear condition/time label conventions pass. Quantitative units/calibration, third-suffix meaning and donor provenance remain open. No design or fit is launched. The chip descriptor has inconsistent concentration labels and is outside the donor unit entirely, so its typos do not choose assay units or conditions. This source may support a future controlled ex-vivo response test only after a separate scientific protocol and measurement contract; it does not solve human clinical diet generalization.

Sources inspected:
- Primary https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0254004
- Deposit and sample-code descriptor https://plos.figshare.com/articles/dataset/Raw_SCFA_dataset_/15030202
- Live rights/files descriptor https://api.figshare.com/v2/articles/15030202
- Workbook https://ndownloader.figshare.com/files/28907155

The metadata pattern correction follows a recorded parsing failure, not a changed outcome criterion. All aggregate flags are in results/gurry_exvivo_ID_census_20261007.json. Biological effects, power, predictive gains and useful-win status were not evaluated.

## Push-gate incident and diagnosis
The initial full-suite run before publication failed in the existing archived-table test because its unchanged live source URL read timed out after35seconds. A command sequence accidentally continued to push despite the nonzero pytest exit. This process failure was reported immediately; no rollback or force push was made. The parent-version script is byte-identical on that path, and its exact assertions pass on a subsequent run against unchanged data. A current full-suite rerun passes487tests/1skip. This evidence identifies a transient network read failure rather than a Gurry metadata regression, but the failed run is not erased.

A permanent scripts/verified_push.py wrapper now runs the fresh full suite, blocks all git actions on a nonzero suite exit, rejects dirty/unreadable trees, performs at most one push and checks exact remote HEAD readback. Offline fixtures assert that failed tests and dirty state never reach a push and that a mismatched remote cannot be reported verified. Future pushes use this wrapper, not a semicolon chain. A temporary parent-source copy initially resolved its ROOT under/tmp and failed to find the manifest; correcting ROOT to the unchanged repository enabled the parent-version check. That diagnostic-path error is not a scientific rerun.

## Primary donor-count clarification
The Human participants section specifies14female and19male healthy participants,33people total, ages23-38. The longitudinal-stability section explicitly repeats the experiment for8participants at least6months apart; the S2caption identifies5pilot participants. Thus42distinct labels across workbook subsets cannot be interpreted as42independent donors. Exact donor-to-visit mapping is still not supplied by the inspected public metadata. The description partly explains repeated biological sampling, not the identity of every label, and does not justify an outcome-blind split until mapping is established.

Primary supplement descriptions S1-S9 do not provide an exact donor-visit dictionary or clarify the pilot suffixc and concentration normalization. A search surfaced thomasgurry/data_analysis, but no verified primary-paper binding to this repository was found; it is not used as a source of eligibility or units. No external code was executed, no new chemical cells were opened and no person-label equivalence was inferred.

Status at this checkpoint: descriptive ex-vivo source inventory completed; quantitative design blocked by donor-visit lineage, replicate provenance and unit interpretation. Keep this source pending rather than fit a convenient subset. No inference about biological efficacy or absence of effect follows from these metadata failures.
