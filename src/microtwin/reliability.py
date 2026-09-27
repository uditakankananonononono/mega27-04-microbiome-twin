"""Twin Reliability Index evidence collector, without an uncalibrated composite."""
from __future__ import annotations

import math
from numbers import Real

COMPONENTS = ("prediction_accuracy", "interaction_dependence", "uncertainty_calibration",
              "transferability", "robustness")


def reliability_report(components, *, calibration_registry=None, domain=None):
    """Expose component evidence and abstain from a composite unless calibrated.

    A 0-100 index requires a versioned calibration registry fitted on disjoint
    development sources and independently validated for the requested domain.
    A supplied number or arbitrary weights do not pass this gate.
    """
    if not isinstance(components, dict) or set(components) - set(COMPONENTS):
        raise ValueError("unknown reliability components")
    if domain is not None and (not isinstance(domain, str) or not domain.strip()):
        raise ValueError("domain must be a nonempty string or None")
    report = {}
    for name in COMPONENTS:
        item = components.get(name)
        if item is None:
            report[name] = {"status": "missing"}
            continue
        if not isinstance(item, dict) or "value" not in item or "source" not in item:
            raise ValueError(f"{name}: value and source evidence required")
        value = item["value"]
        if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
            raise ValueError(f"{name}: value must be finite")
        if not isinstance(item["source"], str) or not item["source"].strip():
            raise ValueError(f"{name}: evidence source required")
        report[name] = {"status": "reported_unvalidated", "value": float(value),
                        "source": item["source"]}
    ready = all(x["status"] == "reported_unvalidated" for x in report.values())
    # No calibrated registry implementation is shipped: even complete
    # components remain a transparent vector, not a falsely precise index.
    return {"components": report, "twin_reliability_index": None,
            "index_status": "unavailable_no_independently_validated_calibrator",
            "all_components_present": ready,
            "calibration_registry_provided": calibration_registry is not None,
            "domain": domain,
            "note": "This is a research evidence ledger, not a clinical risk score."}
