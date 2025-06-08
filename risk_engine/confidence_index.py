from typing import Dict

def calculate_confidence(inputs: Dict) -> Dict:
    score = 1.0
    rationale = []

    # 1. Input completeness (from governance)
    missing = len(inputs.get("Governance", {}).get("missing_fields", []))
    override = len(inputs.get("Governance", {}).get("input_overrides", []))
    completeness_penalty = (missing * 0.05) + (override * 0.03)
    if completeness_penalty > 0:
        rationale.append(f"Completeness penalty: -{round(completeness_penalty*100)}% (missing: {missing}, overrides: {override})")
    score -= completeness_penalty

    # 2. SLA volatility
    volatility = inputs.get("SLA_volatility", 3.0)
    if volatility > 5:
        score -= 0.1
        rationale.append("SLA volatility > 5%: -10% confidence")

    # 3. Incident penalty
    incidents = inputs.get("num_incidents_last_year", 0)
    if incidents > 0:
        incident_penalty = min(0.2, incidents * 0.05)
        score -= incident_penalty
        rationale.append(f"{incidents} incidents last year: -{round(incident_penalty*100)}%")

    # 4. Fallback boost
    fallback = inputs.get("fallback", "medium").lower()
    fallback_boost = {
        "high": 0.05,
        "medium": 0.02,
        "low": 0.0
    }.get(fallback, 0.0)
    score += fallback_boost
    rationale.append(f"Fallback maturity '{fallback}': +{int(fallback_boost * 100)}%")

    # Final score capped to [0.0, 1.0]
    final = round(max(0.0, min(1.0, score)), 2)

    return {
        "confidence_score": final,
        "confidence_rationale": rationale
    }
