# Subject-map strict-record repair, October 10, 2026

Reproduced defect: checked and calibrated partition guards used default non-strict CSV parsing. An unclosed quoted subject field at EOF was silently accepted and the calibrated route reported exact submitted labels disjoint. Malformed quoting can change the submitted pseudonym instead of rejecting the map, undermining that limited guarantee. This is not evidence of biological identity certification before or after repair.

Both guards now share strict UTF-8 CSV record parsing. Decode and malformed-quote errors produce a fixed message without source labels, paths or parser details. Existing exact header/row/sample coverage, whitespace, hashes and cross-partition overlap checks remain. Quoted commas are supported and matching quoted subjects still trigger overlap refusal.

New regressions exercise unclosed quotes, junk after a closing quote, invalid UTF-8, valid quoted subjects and quoted-subject overlap in checked/calibrated routes. Targeted suite 14 passed. Full fresh suite and guarded push/readback reported separately. No raw participant data, biological source admission, fit, formula, uncertainty claim, manuscript or archived results changed.
