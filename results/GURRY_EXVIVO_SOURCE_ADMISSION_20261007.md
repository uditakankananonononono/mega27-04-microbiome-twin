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
