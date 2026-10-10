# Fresh-install reliability CLI walkthrough, October 10, 2026

Verified: all three metadata reliability commands run from an installed wheel in a new venv outside the source checkout, with PYTHONPATH unset and no scientific runtime packages installed. Inputs are generated synthetic metadata only, with no real grant/source/result claim. This is a working public local CLI path, not a hosted platform, model install certification, clinical deployment or scientific validation.

## Reproduce
From a downloaded/cloned source release, build a wheel (build isolation fetches only setuptools/wheel build dependencies):

```sh
python -m pip wheel --no-deps --wheel-dir dist .
python -m venv /tmp/microtwin-demo-env
/tmp/microtwin-demo-env/bin/python -m pip install --no-deps dist/microtwin-0.1.0-py3-none-any.whl
mkdir /tmp/microtwin-demo-work
cd /tmp/microtwin-demo-work
/tmp/microtwin-demo-env/bin/python -m microtwin.admission_demo evidence
/tmp/microtwin-demo-env/bin/microtwin check-admission-boundary evidence/omm12_quarantine_certificate_20261010.json
/tmp/microtwin-demo-env/bin/microtwin receipt-admission-evidence receipt.json --evidence-dir evidence
/tmp/microtwin-demo-env/bin/microtwin verify-admission-evidence receipt.json --evidence-dir evidence
```

No PYTHONPATH or source-checkout results directory needed after installation. `--no-deps` is appropriate ONLY for this standard-library metadata walkthrough. Full numerical/model commands still require the scientific dependencies declared by the project; they are not tested by this unit and should not be represented as dependency-free.

Actual run: newly created Python 3.10 venv with only microtwin 0.1.0, pip 22.0.2 and setuptools 59.6.0; no site-package inheritance. Built wheel hash 2e00475311ddfdff392d78e4575eb5358181656f02440ccbc9778093b2a064cd for this run's code snapshot (not a permanent release signature). Ran commands from a separate working directory with PYTHONPATH unset. Boundary reports quantitative C1 locked, C2 blocked, C3 not proposed, useful_win not tested; synthetic representation counts are 2,664 ambiguous zeros and zero positives. These synthetic counts are fabricated schema fixtures, not OMM12 source outcomes. Receipt verification returns local_evidence_hashes_and_boundary_match, quantitative_admission=false and source_outcome_access=false.

## Friction found and fixes
1. No explicit build-system: no-isolation build attempted UNKNOWN metadata with the environment's old setuptools and failed on missing bdist_wheel. Fixed pyproject build-system to setuptools>=61/wheel/setuptools.build_meta; isolated pip wheel successfully built microtwin and installed its entry point. Online build-dependency access or pre-provisioned build tools is inherent to that route, not concealed.
2. CLI imported NumPy/pandas/audit before command dispatch, so minimal metadata users could not start without the scientific stack. Fixed to load scientific imports only for non-metadata commands. CLI help and the three reliability commands now use standard library only. Regression runs with Python -S and confirms no scientific modules loaded.
3. Evidence roles pointed to checkout-relative results, which are not wheel package data. Fixed to require explicit --evidence-dir for receipt/verify CLI while retaining exact fixed filenames/roles and all strict checks. No arbitrary input role or outcome parser added. Existing Python API defaults remain compatible; CLI now makes its input location explicit.
4. A researcher had no portable synthetic fixture source. Added `python -m microtwin.admission_demo NEW_DIRECTORY`; it refuses existing directories and creates only marked synthetic documentary/metadata schema fixtures. It authenticates no approval. Real quantitative state is never upgraded by demo output.

## Fail-closed and limits
Existing raw-payload/status/manifest/count/symlink/oversize/malformed rejection remains covered. Additional regressions cover explicit-directory roundtrip, synthetic generator non-overwrite, and no scientific imports in a site-package-free subprocess. Existing evidence receipt still verifies against the same public input artifacts because their bytes and boundary semantics did not change.

Signed authenticity is not supplied: receipt plus accepted-file replacement can evade local hash checks. Consistent synthetic or forged statuses are not a real grant. No numerical distributions, source workbooks/ZIPs, private quarantine or biological fits were accessed here. No historical results, admission protocols or scientific claims changed.
