from typing import Dict

def adjust_lef_with_learning(tef: float, fallback: str, num_incidents_last_year: int) -> Dict:
    rationale = []
    incidents = max(0, num_incidents_last_year)
    fallback = fallback.lower()

    # Dampen incident impact based on fallback maturity
    fallback_mitigation = {
        "high": 0.2,
        "medium": 0.1,
        "low": 0.0
    }.get(fallback, 0.1)

    incident_rate = min(incidents / 5, 1.0)  # Cap at 5/year
    adjustment_factor = 1 + incident_rate * (1 - fallback_mitigation)
    adjusted_lef = tef * adjustment_factor

    if incidents == 0:
        rationale.append("No recent incidents; LEF remains unchanged")
    else:
        rationale.append(f"{incidents} incident(s) recorded; TEF scaled by {round(adjustment_factor, 2)}")

    if fallback_mitigation > 0:
        rationale.append(f"Fallback maturity mitigated TEF amplification by {int(fallback_mitigation * 100)}%")

    return {
        "Adjusted LEF": round(adjusted_lef, 2),
        "LEF Adjustment Factor": round(adjustment_factor, 2),
        "Learning Rationale": rationale
    }
