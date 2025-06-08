from typing import Dict

def modifier_engine(inputs: Dict) -> Dict:
    rationale = []

    sla = min(max(inputs.get("SLA") or 80, 0), 100)
    sla_volatility = inputs.get("SLA_volatility") or 3.0
    rto = max(inputs.get("RTO") or 12, 0.1)
    fallback = str(inputs.get("fallback") or "medium").lower()
    dependency_risk = max(min(inputs.get("dependency_risk") or 0.0, 1.0), 0.0)


    # SLA factor adjustment
    sla_factor = (100 - sla) / 100
    volatility_multiplier = 1.2 if sla_volatility > 5.0 else 1.0
    if volatility_multiplier > 1.0:
        rationale.append("SLA penalty increased due to volatility > 5%")
    sla_factor *= volatility_multiplier

    # Fallback degradation if infrastructure risk exists
    fallback_base = {"low": 1.5, "medium": 1.0, "high": 0.6}.get(fallback, 1.0)
    fallback_factor = fallback_base * (1 + dependency_risk)
    if dependency_risk > 0:
        rationale.append(f"Fallback degraded by {int(dependency_risk * 100)}% due to shared infra")

    # RTO damping
    rto_damping = {"low": 1.0, "medium": 0.8, "high": 0.5}.get(fallback, 1.0)
    rto_factor = (rto / 12) * rto_damping
    rationale.append(f"RTO impact dampened by {rto_damping} due to fallback = {fallback}")

    return {
        "SLA Factor": round(sla_factor, 2),
        "RTO Factor": round(rto_factor, 2),
        "Fallback Factor": round(fallback_factor, 2),
        "Rationale": rationale
    }

