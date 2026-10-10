# Paired-loss strict records repair, October 10, 2026

Reproduced defect: an unclosed quoted source-family label at EOF was silently accepted by default CSV parsing and used to group paired benchmark errors. Composition tables used the same permissive parsing. Both now reject malformed quoting and invalid UTF-8 with fixed privacy-safe errors, before loss computation. Exact row/taxon order, source-family/subject consistency, input hashes and no-normalization requirements remain.

Nine new regressions cover truth/prediction/label inputs under unclosed quotes, trailing quote junk and invalid UTF-8. Targeted paired-loss suite 22 passed. Full fresh guarded publication reported separately. No model fit, source admission, benchmark win, scientific result, manuscript or raw data changed. Supplied labels remain unauthenticated; strict syntax cannot establish biological independence.
