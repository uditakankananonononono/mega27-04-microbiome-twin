# Source-admission input privacy/type repair

Frozen protocol d88a46e. Existing screen-sources repaired; no new parallel admission wrapper.

Confirmed defect: known gate fields could echo nested caller values in observed-reason output; non-string study IDs were string-coerced; unhashable IDs could bypass caught errors during duplicate detection. Added exact type/controlled-label checks and fixed, non-echoing ValueError messages before duplicate hashing or report generation. Missing/unknown stays blocked. Integer 1 cannot become boolean True. Extra fields remain omitted rather than forwarded. Successful complete metadata still means manual review only, never final benchmark eligibility.

Pre-fix regression tests: 43 failed/19 passed, demonstrating the input-handling issues. Final targeted tests: 62 passed. Fresh full suite: 424 passed, one skipped (local Meta2DB source input absent), one existing LightGBM warning, 55.04 seconds. Archived eight-source admission decisions unchanged. No outcomes, new model fits, metrics, paper/Drive edits, hosted service or clinical claims.
