# Nested perturbation design preflight, October 10, 2026

Metadata-only biological/technical design validation now has a strict library and CLI. It never reads outcomes, estimates removal effects or admits an endpoint. OMM12 is a BLOCKED metadata fixture, not a newly validated experiment.

```sh
PYTHONPATH=src python -m microtwin.cli check-nested-perturbation-design results/omm12_nested_design_metadata_20261010.json
```

Blocked design exits 2 and emits coverage/reason counts; malformed metadata exits 2 with a fixed non-echoing error. Metadata-ready synthetic design exits 0 but still needs source evidence review and does not certify intervention or source independence. Command uses standard library only.

## Contract
Strict schema requires submitted study/experiment/biological-unit/technical-unit, condition (control/removal), fixed full-control label, batch/medium/time, removed strain token (null for control), and explicit identity_verified boolean. Unknown fields including numerical outcome payloads are rejected. String labels are bounded, numbers finite, booleans not treated as counts/time. JSON loader refuses duplicates/malformed/oversized input.

Biological identity is keyed by study+experiment+biological_unit and must have one treatment across medium/time/technical labels. Technical duplication is refused. Matching controls require exactly one full-control biological unit in the same experiment/batch/medium/time; multiple controls are marked ambiguous rather than arbitrarily selected. Complete label pairs require the specified number of technical units on both sides. Counts come from distinct declared units, never well-count divided by three. Condition coverage across experiments and minimum complete biological label pairs are screened separately. Submitted identity flags are not authenticated grants or preparation evidence.

## OMM12 fixture
Generated solely from the committed structural Tab1 E-label groups: 222 technical label records; all identity_verified=false. No E/S semantics inferred, no S1new added. Experiment token culture_main and biological key condition+E are explicit proposed bookkeeping labels, not original independent-inoculum certification. Even complete control suffixes cannot pass while identity is unverified. Results saved as `omm12_nested_design_preflight_20261010.json`; reported counts concern design labels only. Nonuniform technical replication/minimum complete-pair coverage also blocks eligibility. No complete twelve-removal rank or independent biological n claimed.

Tests include balanced synthetic two-experiment/three-batch designs; unverified identity; missing technical wells; treatment conflict (including mouse2546-style shared identity across regions); duplicate technical records; missing/ambiguous controls; condition imbalance; raw/unknown fields; CLI non-echoing rejection; and real metadata fixture staying BLOCKED.

## Limits
No new scientific gap closes. Matching batch labels are syntax, not proof of same preparation, and caller-declared verification remains unverified at source level. This narrow contract permits one control per batch/context; other designs need a reviewed version, not a guessed pairing rule. Each study/experiment label still requires lineage review; phases/technical wells cannot become independent source families. No mouse outcome, culture effect, clinical response, twin quality or benchmark win follows from metadata readiness.

Code `src/microtwin/nested_perturbation_design.py`, tests `tests/test_nested_perturbation_design.py`, CLI `check-nested-perturbation-design`. Historical results and frozen OMM12 quantitative boundaries unchanged.
