from typing import Dict
from datetime import datetime, timezone

EXPECTED_FIELDS = {
    "SLA": 80,
    "SLA_volatility": 3.0,
    "RTO": 12,
    "fallback": "medium",
    "dependency_risk": 0.0,
    "direct_loss": 50000,
    "seed": 42,
    "num_incidents_last_year": 0
}

def generate_audit_metadata(inputs: Dict) -> Dict:
    audit = {
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model_phase_version": "phase1.0+2.0+3.0",
        "input_overrides": [],
        "missing_fields": [],
        "input_quality_score": 1.0
    }

    # Detect overrides and missing fields
    for key, expected in EXPECTED_FIELDS.items():
        if key not in inputs:
            audit["missing_fields"].append(key)
        elif inputs[key] != expected:
            audit["input_overrides"].append(key)

    # Quality scoring: penalize missing or overridden fields
    penalty = 0.1 * len(audit["input_overrides"]) + 0.15 * len(audit["missing_fields"])
    audit["input_quality_score"] = round(max(0.0, 1.0 - penalty), 2)

    return audit
