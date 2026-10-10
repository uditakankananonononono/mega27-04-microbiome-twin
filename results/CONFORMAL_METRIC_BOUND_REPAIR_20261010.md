# Conformal metric-bound repair, October 10, 2026

Reproduced boundary defect: the accepted 1e-10 numerical tolerance on Bray-Curtis errors could return radius 1.00000000005, above the metric maximum. Accepted near-one roundoff is now capped at 1 before the unchanged conformal rank selection; larger out-of-bound errors still fail. Conversion errors, including overflow and nonnumeric private strings, now return a fixed error rather than expose the supplied value or raise inconsistent exception types.

Four regressions cover accepted roundoff, rejection beyond tolerance and three conversion failures. No change to valid in-range ranks, exchangeability limitations, scientific results or biological calibration claims. Full-suite guarded publication reported separately.
